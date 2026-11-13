
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.models.entities import (
    Anio,
    CategoriaProducto,
    EstadoProducto,
    Producto,
    TipoCelebracion,
    UnidadProducto,
)
from app.repositories.json_repository import JsonRepository


# ============================================================
# EXCEPCIONES DE DOMINIO
# ============================================================

class ProductServiceError(Exception):
    """Error base del servicio de gestión de productos."""


class ProductNotFoundError(ProductServiceError):
    """El producto solicitado no existe."""


class ProductAlreadyPurchasedError(ProductServiceError):
    """El producto ya fue comprado y no admite esta operación."""


class ProductNotPurchasedError(ProductServiceError):
    """El producto todavía no ha sido comprado."""


class ProductYearNotFoundError(ProductServiceError):
    """El año solicitado no existe."""


class ProductCelebrationNotFoundError(ProductServiceError):
    """La celebración solicitada no existe."""


class HistoricalProductReadOnlyError(ProductServiceError):
    """No se permiten modificaciones en años históricos."""


# ============================================================
# SERVICIO DE GESTIÓN DE PRODUCTOS
# ============================================================

class ProductService:
    """
    Gestiona el ciclo de vida de los productos.

    La persistencia se delega exclusivamente en JsonRepository.
    """

    def __init__(self, repository: JsonRepository | None = None):
        self.repository = repository or JsonRepository()

    # --------------------------------------------------------
    # REGISTRAR PRODUCTO
    # --------------------------------------------------------

    def register_product(
        self,
        year: int,
        celebration_type: TipoCelebracion,
        name: str,
        category: CategoriaProducto,
        quantity: Decimal,
        unit: UnidadProducto,
        estimated_unit_price: Decimal,
        description: str | None = None,
    ) -> Producto:
        """Registra un producto nuevo en una celebración."""

        document = self.repository.load()
        year_record = self._find_year(document.anios, year)

        self._ensure_editable_year(year_record)

        celebration = self._find_celebration(
            year_record,
            celebration_type,
        )

        now = datetime.now()

        product = Producto(
            id=uuid4(),
            nombre=name,
            descripcion=description,
            categoria=category,
            cantidad=quantity,
            unidad=unit,
            precio_unitario_estimado=estimated_unit_price,
            precio_unitario_real=None,
            estado=EstadoProducto.PENDIENTE,
            fecha_creacion=now,
            fecha_actualizacion=now,
        )

        celebration.productos.append(product)
        self.repository.save(document)

        return product

    # --------------------------------------------------------
    # LISTAR PRODUCTOS
    # --------------------------------------------------------

    def list_products(
        self,
        year: int,
        celebration_type: TipoCelebracion,
    ) -> list[Producto]:
        """Lista los productos de una celebración."""

        document = self.repository.load()
        year_record = self._find_year(document.anios, year)

        celebration = self._find_celebration(
            year_record,
            celebration_type,
        )

        return list(celebration.productos)

    # --------------------------------------------------------
    # CONSULTAR PRODUCTO
    # --------------------------------------------------------

    def get_product(self, product_id: UUID | str) -> Producto:
        """Consulta un producto por su identificador."""

        document = self.repository.load()
        _, _, product = self._find_product(
            document.anios,
            product_id,
        )

        return product

    # --------------------------------------------------------
    # EDITAR PRODUCTO PENDIENTE
    # --------------------------------------------------------

    def update_pending_product(
        self,
        product_id: UUID | str,
        name: str,
        category: CategoriaProducto,
        quantity: Decimal,
        unit: UnidadProducto,
        estimated_unit_price: Decimal,
        description: str | None = None,
    ) -> Producto:
        """
        Actualiza un producto pendiente.

        Conserva su identificador, celebración y estado.
        """

        document = self.repository.load()

        year_record, celebration, current = self._find_product(
            document.anios,
            product_id,
        )

        self._ensure_editable_year(year_record)

        if current.estado == EstadoProducto.COMPRADO:
            raise ProductAlreadyPurchasedError(
                "Un producto comprado no puede editarse como pendiente."
            )

        updated = self._validated_product(
            current,
            {
                "nombre": name,
                "descripcion": description,
                "categoria": category,
                "cantidad": quantity,
                "unidad": unit,
                "precio_unitario_estimado": estimated_unit_price,
                "fecha_actualizacion": datetime.now(),
            },
        )

        self._replace_product(celebration, updated)
        self.repository.save(document)

        return updated

    # --------------------------------------------------------
    # ELIMINAR PRODUCTO PENDIENTE
    # --------------------------------------------------------

    def delete_pending_product(
        self,
        product_id: UUID | str,
    ) -> None:
        """Elimina un producto únicamente si está pendiente."""

        document = self.repository.load()

        year_record, celebration, product = self._find_product(
            document.anios,
            product_id,
        )

        self._ensure_editable_year(year_record)

        if product.estado == EstadoProducto.COMPRADO:
            raise ProductAlreadyPurchasedError(
                "Un producto comprado no puede eliminarse."
            )

        celebration.productos = [
            item
            for item in celebration.productos
            if item.id != product.id
        ]

        self.repository.save(document)

    # --------------------------------------------------------
    # MARCAR PRODUCTO COMO COMPRADO
    # --------------------------------------------------------

    def mark_as_purchased(
        self,
        product_id: UUID | str,
        real_unit_price: Decimal,
    ) -> Producto:
        """
        Marca un producto pendiente como comprado.

        El precio real es obligatorio. Se permite que sea cero.
        """

        document = self.repository.load()

        year_record, celebration, current = self._find_product(
            document.anios,
            product_id,
        )

        self._ensure_editable_year(year_record)

        if current.estado == EstadoProducto.COMPRADO:
            raise ProductAlreadyPurchasedError(
                "El producto ya está marcado como comprado."
            )

        updated = self._validated_product(
            current,
            {
                "estado": EstadoProducto.COMPRADO,
                "precio_unitario_real": real_unit_price,
                "fecha_actualizacion": datetime.now(),
            },
        )

        self._replace_product(celebration, updated)
        self.repository.save(document)

        return updated

    # --------------------------------------------------------
    # CORREGIR PRODUCTO COMPRADO
    # --------------------------------------------------------

    def correct_purchased_product(
        self,
        product_id: UUID | str,
        name: str,
        category: CategoriaProducto,
        quantity: Decimal,
        unit: UnidadProducto,
        estimated_unit_price: Decimal,
        real_unit_price: Decimal,
        description: str | None = None,
    ) -> Producto:
        """
        Corrige los campos editables de un producto comprado.

        No permite modificar:
        - Identificador.
        - Celebración.
        - Estado comprado.

        La validación completa ocurre antes de guardar.
        """

        document = self.repository.load()

        year_record, celebration, current = self._find_product(
            document.anios,
            product_id,
        )

        self._ensure_editable_year(year_record)

        if current.estado != EstadoProducto.COMPRADO:
            raise ProductNotPurchasedError(
                "La corrección de compra solo aplica a productos comprados."
            )

        updated = self._validated_product(
            current,
            {
                "nombre": name,
                "descripcion": description,
                "categoria": category,
                "cantidad": quantity,
                "unidad": unit,
                "precio_unitario_estimado": estimated_unit_price,
                "precio_unitario_real": real_unit_price,
                "fecha_actualizacion": datetime.now(),
            },
        )

        self._replace_product(celebration, updated)
        self.repository.save(document)

        return updated

    # ========================================================
    # MÉTODOS PRIVADOS
    # ========================================================

    @staticmethod
    def _find_year(years: list[Anio], year: int) -> Anio:
        for record in years:
            if record.anio == year:
                return record

        raise ProductYearNotFoundError(
            f"No existe un registro para el año {year}."
        )

    @staticmethod
    def _find_celebration(
        year_record: Anio,
        celebration_type: TipoCelebracion,
    ):
        for celebration in year_record.celebraciones:
            if celebration.tipo == celebration_type:
                return celebration

        raise ProductCelebrationNotFoundError(
            f"No existe la celebración {celebration_type.value} "
            f"en el año {year_record.anio}."
        )

    @classmethod
    def _find_product(
        cls,
        years: list[Anio],
        product_id: UUID | str,
    ) -> tuple[Anio, object, Producto]:
        try:
            normalized_id = UUID(str(product_id))
        except (ValueError, TypeError, AttributeError) as error:
            raise ProductNotFoundError(
                f"El identificador {product_id} no es válido."
            ) from error

        for year_record in years:
            for celebration in year_record.celebraciones:
                for product in celebration.productos:
                    if product.id == normalized_id:
                        return year_record, celebration, product

        raise ProductNotFoundError(
            f"No existe el producto {product_id}."
        )

    @staticmethod
    def _ensure_editable_year(year_record: Anio) -> None:
        if year_record.anio < datetime.now().year:
            raise HistoricalProductReadOnlyError(
                f"El año {year_record.anio} es histórico y solo permite "
                "consultas."
            )

    @staticmethod
    def _validated_product(
        current: Producto,
        changes: dict,
    ) -> Producto:
        """
        Construye y valida una nueva instancia sin modificar
        el producto original.
        """

        data = current.model_dump()
        data.update(changes)

        return Producto.model_validate(data)

    @staticmethod
    def _replace_product(
        celebration,
        updated: Producto,
    ) -> None:
        for index, product in enumerate(celebration.productos):
            if product.id == updated.id:
                celebration.productos[index] = updated
                return

        raise ProductNotFoundError(
            f"No se encontró el producto {updated.id} para actualizar."
        )
