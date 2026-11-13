
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import get_product_service
from app.models.entities import CategoriaProducto, EstadoProducto, TipoCelebracion
from app.schemas.product_schemas import (
    ActualizarProductoRequest,
    CorregirCompraRequest,
    CrearProductoRequest,
    ListaProductosResponse,
    MarcarCompradoRequest,
    ProductoResponse,
)
from app.services.product_service import ProductService


CATEGORY_FILTER_VALUES = {
    "alimentos": CategoriaProducto.ALIMENTOS,
    "bebidas": CategoriaProducto.BEBIDAS,
    "ingredientes": CategoriaProducto.INGREDIENTES,
    "decoracion": CategoriaProducto.DECORACION,
    "desechables_utensilios": CategoriaProducto.DESECHABLES_UTENSILIOS,
    "otros": CategoriaProducto.OTROS,
}


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
    categoria: str | None = Query(default=None),
    estado: Literal["pendiente", "comprado"] | None = Query(default=None),
    buscar: str | None = Query(default=None, min_length=1),
    service: ProductService = Depends(get_product_service),
):
    productos = service.list_products(
        year=anio,
        celebration_type=_get_celebration_type(tipo),
    )

    if categoria:
        categoria_enum = CATEGORY_FILTER_VALUES.get(categoria)
        if categoria_enum is None:
            productos = []
        else:
            productos = [
                producto for producto in productos
                if producto.categoria == categoria_enum
            ]

    if estado:
        estado_enum = EstadoProducto(estado)
        productos = [
            producto for producto in productos
            if producto.estado == estado_enum
        ]

    if buscar:
        termino = buscar.strip().casefold()
        productos = [
            producto for producto in productos
            if termino in producto.nombre.casefold()
            or (producto.descripcion and termino in producto.descripcion.casefold())
        ]

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
