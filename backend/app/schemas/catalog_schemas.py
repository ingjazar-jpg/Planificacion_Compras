
from pydantic import BaseModel


class CatalogoOpcionResponse(BaseModel):
    """Representa una opción de un catálogo controlado."""

    valor: str
    etiqueta: str


class CatalogosResponse(BaseModel):
    """Respuesta completa de los catálogos disponibles."""

    categorias: list[CatalogoOpcionResponse]
    unidades: list[CatalogoOpcionResponse]
    estados: list[CatalogoOpcionResponse]
