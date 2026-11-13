
from datetime import datetime
from decimal import Decimal

import pytest

from app.models.entities import TipoCelebracion
from app.repositories.json_repository import JsonRepository
from app.services.year_service import (
    HistoricalYearReadOnlyError,
    YearAlreadyExistsError,
    YearNotFoundError,
    YearService,
)


@pytest.fixture
def service(tmp_path):
    repository = JsonRepository(tmp_path / "datos.json")
    return YearService(repository)


def test_create_year(service):
    year = datetime.now().year + 1

    result = service.create_year(
        year=year,
        general_budget=Decimal("2000000.00"),
        christmas_budget=Decimal("1200000.00"),
        new_year_budget=Decimal("800000.00"),
    )

    assert result.anio == year
    assert len(result.celebraciones) == 2
    assert result.presupuesto_general == Decimal("2000000.00")


def test_create_year_with_zero_budgets(service):
    year = datetime.now().year + 1

    result = service.create_year(
        year=year,
        general_budget=Decimal("0"),
        christmas_budget=Decimal("0"),
        new_year_budget=Decimal("0"),
    )

    assert result.presupuesto_general is None
    assert all(
        item.presupuesto is None
        for item in result.celebraciones
    )


def test_create_duplicate_year(service):
    year = datetime.now().year + 1

    service.create_year(year)

    with pytest.raises(YearAlreadyExistsError):
        service.create_year(year)


def test_list_years(service):
    current_year = datetime.now().year

    service.create_year(current_year + 2)
    service.create_year(current_year + 1)

    result = service.list_years()

    assert [item.anio for item in result] == [
        current_year + 1,
        current_year + 2,
    ]


def test_get_year(service):
    year = datetime.now().year + 1
    service.create_year(year)

    result = service.get_year(year)

    assert result.anio == year


def test_get_nonexistent_year(service):
    with pytest.raises(YearNotFoundError):
        service.get_year(1900)


def test_update_general_budget(service):
    year = datetime.now().year + 1
    service.create_year(year)

    result = service.update_general_budget(
        year,
        Decimal("2500000.00"),
    )

    assert result.presupuesto_general == Decimal("2500000.00")


def test_update_christmas_budget(service):
    year = datetime.now().year + 1
    service.create_year(year)

    result = service.update_celebration_budget(
        year,
        TipoCelebracion.NAVIDAD,
        Decimal("1300000.00"),
    )

    christmas = next(
        item
        for item in result.celebraciones
        if item.tipo == TipoCelebracion.NAVIDAD
    )

    assert christmas.presupuesto == Decimal("1300000.00")


def test_update_new_year_budget(service):
    year = datetime.now().year + 1
    service.create_year(year)

    result = service.update_celebration_budget(
        year,
        TipoCelebracion.FIN_DE_ANIO,
        Decimal("900000.00"),
    )

    new_year = next(
        item
        for item in result.celebraciones
        if item.tipo == TipoCelebracion.FIN_DE_ANIO
    )

    assert new_year.presupuesto == Decimal("900000.00")


def test_historical_year_is_read_only(service):
    with pytest.raises(HistoricalYearReadOnlyError):
        service.create_year(datetime.now().year - 1)


def test_historical_year_cannot_update_budget(service):
    year = datetime.now().year + 1
    service.create_year(year)

    repository = service.repository
    document = repository.load()

    document.anios[0].anio = datetime.now().year - 1
    repository.save(document)

    with pytest.raises(HistoricalYearReadOnlyError):
        service.update_general_budget(
            datetime.now().year - 1,
            Decimal("100000.00"),
        )
