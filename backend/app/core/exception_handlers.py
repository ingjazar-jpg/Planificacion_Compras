
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.services.year_service import (
    CelebrationNotFoundError,
    HistoricalYearReadOnlyError,
    YearAlreadyExistsError,
    YearNotFoundError,
)

from app.services.product_service import (
    HistoricalProductReadOnlyError,
    ProductAlreadyPurchasedError,
    ProductCelebrationNotFoundError,
    ProductNotFoundError,
    ProductNotPurchasedError,
    ProductYearNotFoundError,
)


def _error_response(
    status_code: int,
    codigo: str,
    mensaje: str,
    detalles: list | None = None,
) -> JSONResponse:
    content = {
        "error": {
            "codigo": codigo,
            "mensaje": mensaje,
            "detalles": detalles or [],
        }
    }

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(content),
    )

def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores de excepciones de dominio y validación."""

    # ========================================================
    # EXCEPCIONES DE AÑOS
    # ========================================================

    @app.exception_handler(YearNotFoundError)
    async def year_not_found_handler(
        request: Request,
        exc: YearNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "ANIO_NO_ENCONTRADO",
            str(exc),
        )

    @app.exception_handler(YearAlreadyExistsError)
    async def year_already_exists_handler(
        request: Request,
        exc: YearAlreadyExistsError,
    ) -> JSONResponse:
        return _error_response(
            409,
            "ANIO_DUPLICADO",
            str(exc),
        )

    @app.exception_handler(HistoricalYearReadOnlyError)
    async def historical_year_handler(
        request: Request,
        exc: HistoricalYearReadOnlyError,
    ) -> JSONResponse:
        return _error_response(
            400,
            "ANIO_SOLO_LECTURA",
            str(exc),
        )

    @app.exception_handler(CelebrationNotFoundError)
    async def celebration_not_found_handler(
        request: Request,
        exc: CelebrationNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "CELEBRACION_NO_ENCONTRADA",
            str(exc),
        )

    # ========================================================
    # EXCEPCIONES DE PRODUCTOS Y COMPRAS
    # ========================================================

    @app.exception_handler(ProductNotFoundError)
    async def product_not_found_handler(
        request: Request,
        exc: ProductNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "PRODUCTO_NO_ENCONTRADO",
            str(exc),
        )

    @app.exception_handler(ProductYearNotFoundError)
    async def product_year_not_found_handler(
        request: Request,
        exc: ProductYearNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "ANIO_NO_ENCONTRADO",
            str(exc),
        )

    @app.exception_handler(ProductCelebrationNotFoundError)
    async def product_celebration_not_found_handler(
        request: Request,
        exc: ProductCelebrationNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "CELEBRACION_NO_ENCONTRADA",
            str(exc),
        )

    @app.exception_handler(ProductAlreadyPurchasedError)
    async def product_already_purchased_handler(
        request: Request,
        exc: ProductAlreadyPurchasedError,
    ) -> JSONResponse:
        return _error_response(
            409,
            "PRODUCTO_YA_COMPRADO",
            str(exc),
        )

    @app.exception_handler(ProductNotPurchasedError)
    async def product_not_purchased_handler(
        request: Request,
        exc: ProductNotPurchasedError,
    ) -> JSONResponse:
        return _error_response(
            409,
            "PRODUCTO_NO_COMPRADO",
            str(exc),
        )

    @app.exception_handler(HistoricalProductReadOnlyError)
    async def historical_product_handler(
        request: Request,
        exc: HistoricalProductReadOnlyError,
    ) -> JSONResponse:
        return _error_response(
            400,
            "ANIO_SOLO_LECTURA",
            str(exc),
        )

    # ========================================================
    # VALIDACIÓN DE SOLICITUDES
    # ========================================================

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return _error_response(
            422,
            "DATOS_INVALIDOS",
            "La solicitud contiene datos inválidos.",
            exc.errors(),
        )
