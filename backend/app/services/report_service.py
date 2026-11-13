
from decimal import Decimal

from app.models.entities import (
    Anio,
    CategoriaProducto,
    Celebracion,
    EstadoProducto,
)

from app.services.calculation_service import (
    avance_compras,
    gasto_real_celebracion,
    gasto_real_general,
    indicadores_celebracion,
    indicadores_anio,
)

CERO = Decimal("0.00")
UMBRAL_ALERTA = Decimal("0.80")
DOS_DECIMALES = Decimal("0.01")


def formato_decimal(valor: Decimal | None) -> str | None:
    """Convierte un importe Decimal a una cadena con dos decimales."""
    if valor is None:
        return None
    return str(valor.quantize(DOS_DECIMALES))


class ReportService:
    """Servicio de cálculos y reportes del sistema de compras."""

    @staticmethod
    def costo_estimado_producto(producto) -> Decimal:
        """Calcula el costo estimado total de un producto."""
        return producto.cantidad * producto.precio_unitario_estimado

    @classmethod
    def gasto_estimado_celebracion(
        cls,
        celebracion: Celebracion,
    ) -> Decimal:
        """Proyecta el costo de los productos que siguen pendientes."""
        return sum(
            (
                cls.costo_estimado_producto(producto)
                for producto in celebracion.productos
                if producto.estado == EstadoProducto.PENDIENTE
            ),
            start=CERO,
        )

    @classmethod
    def gasto_estimado_general(cls, anio: Anio) -> Decimal:
        """Suma la proyección de las celebraciones del año."""
        return sum(
            (
                cls.gasto_estimado_celebracion(celebracion)
                for celebracion in anio.celebraciones
            ),
            start=CERO,
        )

    @staticmethod
    def _alcance_celebracion(celebracion: Celebracion) -> str:
        """Devuelve el identificador utilizado por el contrato de alertas."""
        identificadores = {
            "Navidad": "navidad",
            "Fin de Año": "fin_anio",
        }
        return identificadores[celebracion.tipo.value]

    @staticmethod
    def _alertas_presupuesto(
        presupuesto: Decimal | None,
        gasto_real: Decimal,
        alcance: str,
    ) -> list[dict]:
        """Genera alertas de consumo y exceso de presupuesto."""
        alertas = []

        if presupuesto is None or presupuesto <= CERO:
            return alertas

        porcentaje = gasto_real / presupuesto * Decimal("100")

        if gasto_real >= presupuesto * UMBRAL_ALERTA:
            alertas.append(
                {
                    "codigo": "PRESUPUESTO_80",
                    "tipo": "preventiva",
                    "alcance": alcance,
                    "mensaje": "Se ha utilizado el 80% del presupuesto.",
                    "porcentaje_consumido": formato_decimal(porcentaje),
                }
            )

        if gasto_real > presupuesto:
            alertas.append(
                {
                    "codigo": "PRESUPUESTO_EXCEDIDO",
                    "alcance": alcance,
                    "mensaje": "El gasto real ha superado el presupuesto.",
                }
            )

        return alertas

    @classmethod
    def generar_alertas(cls, anio: Anio) -> list[dict]:
        """Genera alertas dinámicas sin almacenarlas en el repositorio."""
        alertas = []

        alertas.extend(
            cls._alertas_presupuesto(
                anio.presupuesto_general,
                gasto_real_general(anio),
                "general",
            )
        )

        for celebracion in anio.celebraciones:
            alcance = cls._alcance_celebracion(celebracion)

            alertas.extend(
                cls._alertas_presupuesto(
                    celebracion.presupuesto,
                    gasto_real_celebracion(celebracion),
                    alcance,
                )
            )

            if (
                anio.presupuesto_general is not None
                and celebracion.presupuesto is not None
                and celebracion.presupuesto > anio.presupuesto_general
            ):
                alertas.append(
                    {
                        "codigo": "ASIGNACION_SUPERIOR_GENERAL",
                        "alcance": alcance,
                        "mensaje": (
                            "La asignación de la celebración supera "
                            "el presupuesto general."
                        ),
                    }
                )

        return alertas

    @classmethod
    def dashboard(cls, anio: Anio) -> dict:
        """Construye el dashboard general del año."""
        indicadores = indicadores_anio(anio)
        gasto_estimado = cls.gasto_estimado_general(anio)

        celebraciones = {}

        for celebracion in anio.celebraciones:
            datos = indicadores_celebracion(celebracion)

            comprados = sum(
                1
                for producto in celebracion.productos
                if producto.estado == EstadoProducto.COMPRADO
            )
            pendientes = sum(
                1
                for producto in celebracion.productos
                if producto.estado == EstadoProducto.PENDIENTE
            )

            celebraciones[
                cls._alcance_celebracion(celebracion)
            ] = {
                "presupuesto": formato_decimal(celebracion.presupuesto),
                "gasto_real": formato_decimal(datos["gasto_real"]),
                "saldo": formato_decimal(datos["saldo"]),
                "gasto_estimado": formato_decimal(
                    cls.gasto_estimado_celebracion(celebracion)
                ),
                "productos_comprados": comprados,
                "productos_pendientes": pendientes,
                "avance_compras": formato_decimal(
                    avance_compras(celebracion)
                ),
            }

        return {
            "anio": anio.anio,
            "presupuesto_general": formato_decimal(
                anio.presupuesto_general
            ),
            "gasto_real_general": formato_decimal(
                indicadores["gasto_real"]
            ),
            "saldo_general": formato_decimal(
                indicadores["saldo"]
            ),
            "gasto_estimado_general": formato_decimal(gasto_estimado),
            "celebraciones": celebraciones,
            "alertas": cls.generar_alertas(anio),
        }

    @classmethod
    def resumen_celebracion(
        cls,
        anio: Anio,
        tipo: str,
    ) -> dict:
        """Construye el resumen individual de una celebración."""

        tipos = {
            "navidad": "Navidad",
            "fin_anio": "Fin de Año",
        }

        tipo_nombre = tipos[tipo]

        celebracion = next(
            (
                item
                for item in anio.celebraciones
                if item.tipo.value == tipo_nombre
            ),
            None,
        )

        if celebracion is None:
            raise ValueError(
                f"No existe la celebración {tipo_nombre} en el año."
            )

        indicadores = indicadores_celebracion(celebracion)

        comprados = sum(
            1
            for producto in celebracion.productos
            if producto.estado == EstadoProducto.COMPRADO
        )

        pendientes = sum(
            1
            for producto in celebracion.productos
            if producto.estado == EstadoProducto.PENDIENTE
        )

        alertas = [
            alerta
            for alerta in cls.generar_alertas(anio)
            if alerta["alcance"] == tipo
        ]

        return {
            "anio": anio.anio,
            "tipo": tipo,
            "presupuesto": formato_decimal(
                celebracion.presupuesto
            ),
            "gasto_real": formato_decimal(
                indicadores["gasto_real"]
            ),
            "saldo": formato_decimal(
                indicadores["saldo"]
            ),
            "gasto_estimado": formato_decimal(
                cls.gasto_estimado_celebracion(celebracion)
            ),
            "productos_comprados": comprados,
            "productos_pendientes": pendientes,
            "avance_compras": formato_decimal(
                avance_compras(celebracion)
            ),
            "alertas": alertas,
        }

    @classmethod
    def estadisticas_categorias(cls, anio: Anio) -> dict:
        """Calcula la distribución de productos y gastos por categoría."""

        gasto_general = gasto_real_general(anio)
        categorias = []

        for categoria in CategoriaProducto:
            productos = [
                producto
                for celebracion in anio.celebraciones
                for producto in celebracion.productos
                if producto.categoria == categoria
            ]

            comprados = [
                producto
                for producto in productos
                if producto.estado == EstadoProducto.COMPRADO
            ]

            pendientes = [
                producto
                for producto in productos
                if producto.estado == EstadoProducto.PENDIENTE
            ]

            gasto_real = sum(
                (
                    producto.cantidad * producto.precio_unitario_real
                    for producto in comprados
                    if producto.precio_unitario_real is not None
                ),
                start=CERO,
            )

            gasto_estimado = sum(
                (
                    cls.costo_estimado_producto(producto)
                    for producto in pendientes
                ),
                start=CERO,
            )

            if gasto_general > CERO:
                participacion = (
                    gasto_real / gasto_general * Decimal("100")
                )
            else:
                participacion = CERO

            categorias.append(
                {
                    "categoria": categoria.value,
                    "productos_total": len(productos),
                    "productos_comprados": len(comprados),
                    "productos_pendientes": len(pendientes),
                    "gasto_real": formato_decimal(gasto_real),
                    "gasto_estimado": formato_decimal(gasto_estimado),
                    "participacion_porcentual": formato_decimal(
                        participacion
                    ),
                }
            )

        return {
            "anio": anio.anio,
            "gasto_real_general": formato_decimal(gasto_general),
            "categorias": categorias,
        }
