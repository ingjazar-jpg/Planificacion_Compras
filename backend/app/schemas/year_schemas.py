
from datetime import datetime
from decimal import Decimal
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
    TipoCelebracion,
    UnidadProducto,
)


class YearRequestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CrearAnioRequest(YearRequestBase):
    anio: int
    presupuesto_general: Decimal | None = Field(ge=0)
    presupuesto_navidad: Decimal | None = Field(ge=0)
    presupuesto_fin_anio: Decimal | None = Field(ge=0)

    @field_validator(
        "presupuesto_general",
        "presupuesto_navidad",
        "presupuesto_fin_anio",
        mode="before",
    )
    @classmethod
    def validar_presupuestos_como_cadenas(cls, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("El presupuesto debe enviarse como cadena decimal.")
        return value


class PresupuestoGeneralRequest(YearRequestBase):
    presupuesto_general: Decimal | None = Field(ge=0)

    @field_validator("presupuesto_general", mode="before")
    @classmethod
    def validar_presupuesto_como_cadena(cls, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("El presupuesto debe enviarse como cadena decimal.")
        return value


class PresupuestoCelebracionRequest(YearRequestBase):
    presupuesto: Decimal | None = Field(ge=0)
    @field_validator("presupuesto", mode="before")
    @classmethod
    def validar_presupuesto_como_cadena(cls, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("El presupuesto debe enviarse como cadena decimal.")
        return value


class AnioListadoResponse(BaseModel):
    id: UUID
    anio: int
    presupuesto_general: Decimal | None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("presupuesto_general")
    def serializar_presupuesto(self, value):
        return format(value, ".2f") if value is not None else None


class ListaAniosResponse(BaseModel):
    anios: list[AnioListadoResponse]


class ProductoAnioResponse(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)

    @field_serializer(
        "cantidad",
        "precio_unitario_estimado",
        "precio_unitario_real",
    )
    def serializar_decimales(self, value):
        return format(value, ".2f") if value is not None else None


class CelebracionAnioResponse(BaseModel):
    id: UUID
    tipo: TipoCelebracion
    presupuesto: Decimal | None
    productos: list[ProductoAnioResponse]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("presupuesto")
    def serializar_presupuesto(self, value):
        return format(value, ".2f") if value is not None else None


class AnioResponse(BaseModel):
    id: UUID
    anio: int
    presupuesto_general: Decimal | None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    celebraciones: list[CelebracionAnioResponse]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("presupuesto_general")
    def serializar_presupuesto(self, value):
        return format(value, ".2f") if value is not None else None
