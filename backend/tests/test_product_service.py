
from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.entities import (
    CategoriaProducto,
    EstadoProducto,
    TipoCelebracion,
    UnidadProducto,
)
from app.repositories.json_repository import JsonRepository
from app.services.year_service import YearService
from app.services.product_service import (
    HistoricalProductReadOnlyError,
    ProductAlreadyPurchasedError,
    ProductNotFoundError,
    ProductNotPurchasedError,
    ProductService,
)


@pytest.fixture
def setup_services(tmp_path):
    repository = JsonRepository(tmp_path / "datos.json")

    year_service = YearService(repository)
    product_service = ProductService(repository)

    year = datetime.now().year + 1
    year_service.create_year(year)

    return repository, year_service, product_service, year


def register_pending_product(service, year):
    return service.register_product(
        year=year,
        celebration_type=TipoCelebracion.NAVIDAD,
        name="Pollo",
        description="Para la cena familiar",
        category=CategoriaProducto.ALIMENTOS,
        quantity=Decimal("2.50"),
        unit=UnidadProducto.KILOGRAMO,
        estimated_unit_price=Decimal("18000.50"),
    )


def test_register_product(setup_services):
    _, _, service, year = setup_services

    product = register_pending_product(service, year)

    assert product.nombre == "Pollo"
    assert product.estado == EstadoProducto.PENDIENTE
    assert product.precio_unitario_real is None
    assert product.cantidad == Decimal("2.50")


def test_list_products(setup_services):
    _, _, service, year = setup_services

    register_pending_product(service, year)

    products = service.list_products(
        year,
        TipoCelebracion.NAVIDAD,
    )

    assert len(products) == 1
    assert products[0].nombre == "Pollo"


def test_get_product(setup_services):
    _, _, service, year = setup_services

    created = register_pending_product(service, year)
    result = service.get_product(created.id)

    assert result.id == created.id
    assert result.nombre == "Pollo"


def test_get_nonexistent_product(setup_services):
    _, _, service, _ = setup_services

    with pytest.raises(ProductNotFoundError):
        service.get_product("00000000-0000-4000-8000-000000000001")


def test_update_pending_product(setup_services):
    _, _, service, year = setup_services

    product = register_pending_product(service, year)

    updated = service.update_pending_product(
        product_id=product.id,
        name="Pollo entero",
        description="Producto actualizado",
        category=CategoriaProducto.ALIMENTOS,
        quantity=Decimal("3.00"),
        unit=UnidadProducto.KILOGRAMO,
        estimated_unit_price=Decimal("19000.00"),
    )

    assert updated.id == product.id
    assert updated.nombre == "Pollo entero"
    assert updated.estado == EstadoProducto.PENDIENTE
    assert updated.cantidad == Decimal("3.00")


def test_delete_pending_product(setup_services):
    _, _, service, year = setup_services

    product = register_pending_product(service, year)

    service.delete_pending_product(product.id)

    with pytest.raises(ProductNotFoundError):
        service.get_product(product.id)


def test_mark_product_as_purchased(setup_services):
    _, _, service, year = setup_services

    product = register_pending_product(service, year)

    updated = service.mark_as_purchased(
        product.id,
        Decimal("20000.75"),
    )

    assert updated.estado == EstadoProducto.COMPRADO
    assert updated.precio_unitario_real == Decimal("20000.75")


def test_mark_product_as_purchased_with_zero_price(setup_services):
    _, _, service, year = setup_services

    product = register_pending_product(service, year)

    updated = service.mark_as_purchased(
        product.id,
        Decimal("0"),
    )

    assert updated.estado == EstadoProducto.COMPRADO
    assert updated.precio_unitario_real == Decimal("0")


def test_cannot_delete_purchased_product(setup_services):
    _, _, service, year = setup_services

    product = register_pending_product(service, year)
    service.mark_as_purchased(product.id, Decimal("20000"))

    with pytest.raises(ProductAlreadyPurchasedError):
        service.delete_pending_product(product.id)


def test_cannot_mark_purchased_product_again(setup_services):
    _, _, service, year = setup_services

    product = register_pending_product(service, year)
    service.mark_as_purchased(product.id, Decimal("20000"))

    with pytest.raises(ProductAlreadyPurchasedError):
        service.mark_as_purchased(product.id, Decimal("21000"))


def test_correct_purchased_product(setup_services):
    _, _, service, year = setup_services

    product = register_pending_product(service, year)
    service.mark_as_purchased(product.id, Decimal("20000"))

    corrected = service.correct_purchased_product(
        product_id=product.id,
        name="Pollo entero",
        description="Producto corregido",
        category=CategoriaProducto.ALIMENTOS,
        quantity=Decimal("3.00"),
        unit=UnidadProducto.KILOGRAMO,
        estimated_unit_price=Decimal("19000"),
        real_unit_price=Decimal("21000"),
    )

    assert corrected.id == product.id
    assert corrected.nombre == "Pollo entero"
    assert corrected.estado == EstadoProducto.COMPRADO
    assert corrected.precio_unitario_real == Decimal("21000")
    assert corrected.cantidad == Decimal("3.00")


def test_correction_does_not_allow_pending_product(setup_services):
    _, _, service, year = setup_services

    product = register_pending_product(service, year)

    with pytest.raises(ProductNotPurchasedError):
        service.correct_purchased_product(
            product_id=product.id,
            name="Pollo corregido",
            description=None,
            category=CategoriaProducto.ALIMENTOS,
            quantity=Decimal("3"),
            unit=UnidadProducto.KILOGRAMO,
            estimated_unit_price=Decimal("19000"),
            real_unit_price=Decimal("21000"),
        )


def test_invalid_correction_does_not_modify_product(setup_services):
    _, _, service, year = setup_services

    product = register_pending_product(service, year)
    service.mark_as_purchased(product.id, Decimal("20000"))

    with pytest.raises(ValidationError):
        service.correct_purchased_product(
            product_id=product.id,
            name="Pollo corregido",
            description=None,
            category=CategoriaProducto.ALIMENTOS,
            quantity=Decimal("0"),
            unit=UnidadProducto.KILOGRAMO,
            estimated_unit_price=Decimal("19000"),
            real_unit_price=Decimal("21000"),
        )

    unchanged = service.get_product(product.id)

    assert unchanged.nombre == "Pollo"
    assert unchanged.cantidad == Decimal("2.50")
    assert unchanged.precio_unitario_real == Decimal("20000")


def test_historical_product_cannot_be_modified(setup_services):
    repository, _, service, year = setup_services

    product = register_pending_product(service, year)

    document = repository.load()
    document.anios[0].anio = datetime.now().year - 1
    repository.save(document)

    with pytest.raises(HistoricalProductReadOnlyError):
        service.mark_as_purchased(
            product.id,
            Decimal("20000"),
        )
