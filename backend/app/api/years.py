
from typing import Literal

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_year_service
from app.models.entities import TipoCelebracion
from app.schemas.year_schemas import (
    AnioResponse,
    CrearAnioRequest,
    ListaAniosResponse,
    PresupuestoCelebracionRequest,
    PresupuestoGeneralRequest,
)
from app.services.year_service import YearService


router = APIRouter(
    prefix="/anios",
    tags=["Años"],
)


@router.post(
    "",
    response_model=AnioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear año",
)
def crear_anio(
    solicitud: CrearAnioRequest,
    year_service: YearService = Depends(get_year_service),
):
    return year_service.create_year(
        year=solicitud.anio,
        general_budget=solicitud.presupuesto_general,
        christmas_budget=solicitud.presupuesto_navidad,
        new_year_budget=solicitud.presupuesto_fin_anio,
    )


@router.get(
    "",
    response_model=ListaAniosResponse,
    summary="Listar años",
)
def listar_anios(
    year_service: YearService = Depends(get_year_service),
):
    registros = year_service.list_years()

    return {
        "anios": [
            {
                "id": registro.id,
                "anio": registro.anio,
                "presupuesto_general": registro.presupuesto_general,
            }
            for registro in registros
        ]
    }


@router.get(
    "/{anio}",
    response_model=AnioResponse,
    summary="Consultar año",
)
def consultar_anio(
    anio: int,
    year_service: YearService = Depends(get_year_service),
):
    return year_service.get_year(anio)


@router.put(
    "/{anio}/presupuesto-general",
    response_model=AnioResponse,
    summary="Actualizar presupuesto general",
)
def actualizar_presupuesto_general(
    anio: int,
    solicitud: PresupuestoGeneralRequest,
    year_service: YearService = Depends(get_year_service),
):
    return year_service.update_general_budget(
        year=anio,
        budget=solicitud.presupuesto_general,
    )


@router.put(
    "/{anio}/celebraciones/{tipo}/presupuesto",
    response_model=AnioResponse,
    summary="Actualizar presupuesto de celebración",
)
def actualizar_presupuesto_celebracion(
    anio: int,
    tipo: Literal["navidad", "fin_anio"],
    solicitud: PresupuestoCelebracionRequest,
    year_service: YearService = Depends(get_year_service),
):
    tipos = {
        "navidad": TipoCelebracion.NAVIDAD,
        "fin_anio": TipoCelebracion.FIN_DE_ANIO,
    }

    return year_service.update_celebration_budget(
        year=anio,
        celebration_type=tipos[tipo],
        budget=solicitud.presupuesto,
    )
