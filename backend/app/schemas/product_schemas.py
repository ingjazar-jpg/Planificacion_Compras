
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

from app.models.entities import (
    CategoriaProducto,
    EstadoProducto,
    UnidadProducto,
)


class ProductRequestBase(BaseModel):
    """Campos compartidos para registrar y editar productos."""

    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1)
    descripcion: str | None = None
    categoria: CategoriaProducto
    cantidad: Decimal = Field(gt=0)
    unidad: UnidadProducto
    precio_unitario_estimado: Decimal = Field(ge=0)

    @field_validator(
        "cantidad",
        "precio_unitario_estimado",
        mode="before",
    )
    @classmethod
    def validate_decimal_strings(cls, value: object) -> Decimal:
        if not isinstance(value, str):
            raise ValueError("El valor debe enviarse como cadena decimal.")

        try:
            number = Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValueError("El valor no es un decimal válido.")

        if not number.is_finite():
            raise ValueError("El valor debe ser un decimal finito.")

        return number

    @field_validator("nombre")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre del producto es obligatorio.")
        return value


class CrearProductoRequest(ProductRequestBase):
    """Datos necesarios para registrar un producto."""


class ActualizarProductoRequest(ProductRequestBase):
    """Datos para editar un producto pendiente."""


class MarcarCompradoRequest(BaseModel):
    """Datos necesarios para marcar un producto como comprado."""

    model_config = ConfigDict(extra="forbid")

    precio_unitario_real: Decimal = Field(ge=0)

    @field_validator("precio_unitario_real", mode="before")
    @classmethod
    def validate_real_price(cls, value: object) -> Decimal:
        if not isinstance(value, str):
            raise ValueError("El precio real debe enviarse como cadena decimal.")

        try:
            number = Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValueError("El precio real no es un decimal válido.")

        if not number.is_finite():
            raise ValueError("El precio real debe ser un decimal finito.")

        return number


class CorregirCompraRequest(ProductRequestBase):
    """Datos para corregir un producto que ya fue comprado."""

    precio_unitario_real: Decimal = Field(ge=0)

    @field_validator("precio_unitario_real", mode="before")
    @classmethod
    def validate_real_price(cls, value: object) -> Decimal:
        if not isinstance(value, str):
            raise ValueError("El precio real debe enviarse como cadena decimal.")

        try:
            number = Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValueError("El precio real no es un decimal válido.")

        if not number.is_finite():
            raise ValueError("El precio real debe ser un decimal finito.")

        return number


class ProductoResponse(BaseModel):
    """Representación pública de un producto."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str
    descripcion: str | None
    categoria: CategoriaProducto
    cantidad: Decimal
    unidad: UnidadProducto
    precio_unitario_estimado: Decimal
    precio_unitario_real: Decimal | None
    estado: EstadoProducto
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    @field_serializer(
        "cantidad",
        "precio_unitario_estimado",
        "precio_unitario_real",
        when_used="json",
    )
    def serialize_decimal(self, value: Decimal | None) -> str | None:
        return str(value) if value is not None else None


class ListaProductosResponse(BaseModel):
    """Respuesta de consulta de productos."""

    productos: list[ProductoResponse]
