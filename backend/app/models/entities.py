
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    UUID4,
    field_validator,
    model_validator,
)


# ============================================================
# ENUMERACIONES
# ============================================================

class TipoCelebracion(str, Enum):
    NAVIDAD = "Navidad"
    FIN_DE_ANIO = "Fin de Año"


class CategoriaProducto(str, Enum):
    ALIMENTOS = "Alimentos"
    BEBIDAS = "Bebidas"
    INGREDIENTES = "Ingredientes"
    DECORACION = "Decoración"
    DESECHABLES_UTENSILIOS = "Desechables y utensilios"
    OTROS = "Otros"


class UnidadProducto(str, Enum):
    UNIDAD = "Unidad"
    KILOGRAMO = "Kilogramo"
    GRAMO = "Gramo"
    LITRO = "Litro"
    MILILITRO = "Mililitro"
    PAQUETE = "Paquete"
    BOTELLA = "Botella"
    DOCENA = "Docena"
    OTRO = "Otro"


class EstadoProducto(str, Enum):
    PENDIENTE = "pendiente"
    COMPRADO = "comprado"


# ============================================================
# CONFIGURACIÓN BASE
# ============================================================

class ModeloBase(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )


# ============================================================
# PRODUCTO
# ============================================================

class Producto(ModeloBase):
    id: UUID4
    nombre: str
    descripcion: str | None = None
    categoria: CategoriaProducto
    cantidad: Decimal = Field(gt=0)
    unidad: UnidadProducto
    precio_unitario_estimado: Decimal = Field(ge=0)
    precio_unitario_real: Decimal | None = Field(default=None, ge=0)
    estado: EstadoProducto
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    @model_validator(mode="after")
    def validar_estado_y_precio_real(self):
        if (
            self.estado == EstadoProducto.PENDIENTE
            and self.precio_unitario_real is not None
        ):
            raise ValueError(
                "Un producto pendiente no puede tener precio real."
            )

        if (
            self.estado == EstadoProducto.COMPRADO
            and self.precio_unitario_real is None
        ):
            raise ValueError(
                "Un producto comprado debe tener precio real registrado."
            )

        return self


# ============================================================
# CELEBRACIÓN
# ============================================================

class Celebracion(ModeloBase):
    id: UUID4
    tipo: TipoCelebracion
    presupuesto: Decimal | None = Field(default=None, ge=0)
    productos: list[Producto] = Field(default_factory=list)

    @field_validator("presupuesto")
    @classmethod
    def normalizar_presupuesto(cls, valor):
        if valor == Decimal("0"):
            return None
        return valor


# ============================================================
# AÑO
# ============================================================

class Anio(ModeloBase):
    id: UUID4
    anio: int
    presupuesto_general: Decimal | None = Field(default=None, ge=0)
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    celebraciones: list[Celebracion]

    @field_validator("presupuesto_general")
    @classmethod
    def normalizar_presupuesto(cls, valor):
        if valor == Decimal("0"):
            return None
        return valor

    @model_validator(mode="after")
    def validar_celebraciones(self):
        tipos = [celebracion.tipo for celebracion in self.celebraciones]

        tipos_requeridos = {
            TipoCelebracion.NAVIDAD,
            TipoCelebracion.FIN_DE_ANIO,
        }

        if len(tipos) != 2 or set(tipos) != tipos_requeridos:
            raise ValueError(
                "Cada año debe contener exactamente una celebración "
                "de Navidad y una de Fin de Año."
            )

        return self


# ============================================================
# METADATOS Y DOCUMENTO PRINCIPAL
# ============================================================

class Metadata(ModeloBase):
    schema_version: Literal["1.0"]


class DatosCompras(ModeloBase):
    metadata: Metadata
    anios: list[Anio]

    @model_validator(mode="after")
    def validar_anios_unicos(self):
        numeros_anios = [registro.anio for registro in self.anios]

        if len(numeros_anios) != len(set(numeros_anios)):
            raise ValueError("No se permiten años duplicados.")

        return self
