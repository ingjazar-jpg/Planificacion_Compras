
from typing import Literal

from fastapi import APIRouter, Depends

from app.api.dependencies import get_year_service
from app.schemas.report_schemas import (
    DashboardResponse,
    EstadisticasCategoriasResponse,
    ResumenCelebracionResponse,
)
from app.services.report_service import ReportService
from app.services.year_service import YearService


router = APIRouter(
    prefix="/anios",
    tags=["Reportes"],
)


@router.get(
    "/{anio}/dashboard",
    response_model=DashboardResponse,
    summary="Consultar dashboard general",
    description="Obtiene los indicadores generales y alertas de un año.",
)
def obtener_dashboard(
    anio: int,
    year_service: YearService = Depends(get_year_service),
) -> dict:
    """Consulta el año y construye su dashboard."""

    registro = year_service.get_year(anio)

    return ReportService.dashboard(registro)


@router.get(
    "/{anio}/celebraciones/{tipo}/resumen",
    response_model=ResumenCelebracionResponse,
    summary="Consultar resumen de celebración",
    description=(
        "Obtiene los indicadores, gastos y alertas "
        "de una celebración específica."
    ),
)
def obtener_resumen_celebracion(
    anio: int,
    tipo: Literal["navidad", "fin_anio"],
    year_service: YearService = Depends(get_year_service),
) -> dict:
    """Consulta el resumen de una celebración."""

    registro = year_service.get_year(anio)

    return ReportService.resumen_celebracion(
        registro,
        tipo,
    )


@router.get(
    "/{anio}/estadisticas/categorias",
    response_model=EstadisticasCategoriasResponse,
    summary="Consultar estadísticas por categoría",
    description=(
        "Obtiene la distribución de productos y gastos "
        "por categoría para un año."
    ),
)
def obtener_estadisticas_categorias(
    anio: int,
    year_service: YearService = Depends(get_year_service),
) -> dict:
    """Consulta las estadísticas de categorías."""

    registro = year_service.get_year(anio)

    return ReportService.estadisticas_categorias(registro)
