
from fastapi import FastAPI

from app.api.reports import router as reports_router
from app.api.years import router as years_router
from app.core.exception_handlers import register_exception_handlers
from app.api.products import router as products_router
from app.api.catalogs import router as catalogs_router


app = FastAPI(
    title="Sistema de Planificación y Presupuesto de Compras",
    description=(
        "API para la planificación y gestión de presupuestos "
        "de compras de Navidad y Fin de Año."
    ),
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(
    years_router,
    prefix="/api/v1",
)

app.include_router(
    reports_router,
    prefix="/api/v1",
)
app.include_router(
    products_router,
    prefix="/api/v1"
)

app.include_router(
    catalogs_router,
    prefix="/api/v1",
)