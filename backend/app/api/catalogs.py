
from fastapi import APIRouter

from app.schemas.catalog_schemas import CatalogosResponse


router = APIRouter(
    prefix="/catalogos",
    tags=["Catálogos"],
)


CATALOGOS = {
    "categorias": [
        {"valor": "alimentos", "etiqueta": "Alimentos"},
        {"valor": "bebidas", "etiqueta": "Bebidas"},
        {"valor": "ingredientes", "etiqueta": "Ingredientes"},
        {"valor": "decoracion", "etiqueta": "Decoración"},
        {
            "valor": "desechables_utensilios",
            "etiqueta": "Desechables y utensilios",
        },
        {"valor": "otros", "etiqueta": "Otros"},
    ],
    "unidades": [
        {"valor": "unidad", "etiqueta": "Unidad"},
        {"valor": "kilogramo", "etiqueta": "Kilogramo"},
        {"valor": "gramo", "etiqueta": "Gramo"},
        {"valor": "litro", "etiqueta": "Litro"},
        {"valor": "mililitro", "etiqueta": "Mililitro"},
        {"valor": "paquete", "etiqueta": "Paquete"},
        {"valor": "botella", "etiqueta": "Botella"},
        {"valor": "docena", "etiqueta": "Docena"},
        {"valor": "otro", "etiqueta": "Otro"},
    ],
    "estados": [
        {"valor": "pendiente", "etiqueta": "Pendiente"},
        {"valor": "comprado", "etiqueta": "Comprado"},
    ],
}


@router.get(
    "",
    response_model=CatalogosResponse,
    summary="Consultar catálogos",
    description=(
        "Obtiene las categorías, unidades y estados "
        "disponibles para la gestión de productos."
    ),
)
def obtener_catalogos() -> dict:
    """Devuelve los catálogos controlados por el backend."""

    return CATALOGOS
