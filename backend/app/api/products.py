
from typing import Literal

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_product_service
from app.models.entities import TipoCelebracion
from app.schemas.product_schemas import (
    ActualizarProductoRequest,
    CorregirCompraRequest,
    CrearProductoRequest,
    ListaProductosResponse,
    MarcarCompradoRequest,
    ProductoResponse,
)
from app.services.product_service import ProductService


router = APIRouter(tags=["Productos y compras"])


def _get_celebration_type(
    tipo: Literal["navidad", "fin_anio"],
) -> TipoCelebracion:
    if tipo == "navidad":
        return TipoCelebracion.NAVIDAD

    return TipoCelebracion.FIN_DE_ANIO


@router.post(
    "/anios/{anio}/celebraciones/{tipo}/productos",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_product(
    anio: int,
    tipo: Literal["navidad", "fin_anio"],
    request: CrearProductoRequest,
    service: ProductService = Depends(get_product_service),
):
    return service.register_product(
        year=anio,
        celebration_type=_get_celebration_type(tipo),
        name=request.nombre,
        description=request.descripcion,
        category=request.categoria,
        quantity=request.cantidad,
        unit=request.unidad,
        estimated_unit_price=request.precio_unitario_estimado,
    )


@router.get(
    "/anios/{anio}/celebraciones/{tipo}/productos",
    response_model=ListaProductosResponse,
)
def list_products(
    anio: int,
    tipo: Literal["navidad", "fin_anio"],
    service: ProductService = Depends(get_product_service),
):
    productos = service.list_products(
        year=anio,
        celebration_type=_get_celebration_type(tipo),
    )

    return {"productos": productos}


@router.get(
    "/productos/{producto_id}",
    response_model=ProductoResponse,
)
def get_product(
    producto_id: str,
    service: ProductService = Depends(get_product_service),
):
    return service.get_product(producto_id)


@router.put(
    "/productos/{producto_id}",
    response_model=ProductoResponse,
)
def update_product(
    producto_id: str,
    request: ActualizarProductoRequest,
    service: ProductService = Depends(get_product_service),
):
    return service.update_pending_product(
        product_id=producto_id,
        name=request.nombre,
        description=request.descripcion,
        category=request.categoria,
        quantity=request.cantidad,
        unit=request.unidad,
        estimated_unit_price=request.precio_unitario_estimado,
    )


@router.delete(
    "/productos/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    producto_id: str,
    service: ProductService = Depends(get_product_service),
):
    service.delete_pending_product(producto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/productos/{producto_id}/comprar",
    response_model=ProductoResponse,
)
def mark_product_as_purchased(
    producto_id: str,
    request: MarcarCompradoRequest,
    service: ProductService = Depends(get_product_service),
):
    return service.mark_as_purchased(
        product_id=producto_id,
        real_unit_price=request.precio_unitario_real,
    )


@router.patch(
    "/productos/{producto_id}/correccion-compra",
    response_model=ProductoResponse,
)
def correct_purchased_product(
    producto_id: str,
    request: CorregirCompraRequest,
    service: ProductService = Depends(get_product_service),
):
    return service.correct_purchased_product(
        product_id=producto_id,
        name=request.nombre,
        description=request.descripcion,
        category=request.categoria,
        quantity=request.cantidad,
        unit=request.unidad,
        estimated_unit_price=request.precio_unitario_estimado,
        real_unit_price=request.precio_unitario_real,
    )
