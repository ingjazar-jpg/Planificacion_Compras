
from datetime import datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_product_service
from app.main import app
from app.models.entities import CategoriaProducto, UnidadProducto
from app.repositories.json_repository import JsonRepository
from app.services.product_service import ProductService
from app.services.year_service import YearService


@pytest.fixture
def api_context(tmp_path):
    """Prepara la API con persistencia JSON temporal."""

    repository = JsonRepository(
        tmp_path / "datos_compras_test.json"
    )

    year = datetime.now().year

    year_service = YearService(repository=repository)
    year_service.create_year(
        year=year,
        general_budget=Decimal("1000"),
        christmas_budget=Decimal("500"),
        new_year_budget=Decimal("500"),
    )

    product_service = ProductService(repository=repository)

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_product_service] = (
        lambda: product_service
    )

    try:
        with TestClient(app) as client:
            yield client, year
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


def product_payload(**overrides):
    """Construye una solicitud válida de producto."""

    payload = {
        "nombre": "Cena navideña",
        "descripcion": "Productos para la celebración",
        "categoria": next(iter(CategoriaProducto)).value,
        "cantidad": "2",
        "unidad": next(iter(UnidadProducto)).value,
        "precio_unitario_estimado": "25.50",
    }

    payload.update(overrides)
    return payload


def create_product(client, year):
    """Registra un producto para reutilizarlo en las pruebas."""

    response = client.post(
        f"/api/v1/anios/{year}/celebraciones/navidad/productos",
        json=product_payload(),
    )

    assert response.status_code == 201
    return response.json()


def test_register_list_and_get_product(api_context):
    client, year = api_context

    created = create_product(client, year)

    assert created["nombre"] == "Cena navideña"
    assert created["estado"] == "pendiente"
    assert created["precio_unitario_real"] is None
    assert isinstance(created["id"], str)

    list_response = client.get(
        f"/api/v1/anios/{year}/celebraciones/navidad/productos"
    )

    assert list_response.status_code == 200
    assert len(list_response.json()["productos"]) == 1

    get_response = client.get(
        f"/api/v1/productos/{created['id']}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == created["id"]


def test_update_pending_product(api_context):
    client, year = api_context
    created = create_product(client, year)

    response = client.put(
        f"/api/v1/productos/{created['id']}",
        json=product_payload(
            nombre="Cena actualizada",
            cantidad="3",
            precio_unitario_estimado="30.00",
        ),
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "Cena actualizada"
    assert response.json()["cantidad"] == "3"


def test_delete_pending_product(api_context):
    client, year = api_context
    created = create_product(client, year)

    response = client.delete(
        f"/api/v1/productos/{created['id']}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/productos/{created['id']}"
    )

    assert get_response.status_code == 404
    assert get_response.json()["error"]["codigo"] == (
        "PRODUCTO_NO_ENCONTRADO"
    )


def test_mark_product_as_purchased(api_context):
    client, year = api_context
    created = create_product(client, year)

    response = client.patch(
        f"/api/v1/productos/{created['id']}/comprar",
        json={"precio_unitario_real": "0"},
    )

    assert response.status_code == 200
    assert response.json()["estado"] == "comprado"
    assert response.json()["precio_unitario_real"] == "0"


def test_purchased_product_cannot_be_purchased_or_deleted(api_context):
    client, year = api_context
    created = create_product(client, year)

    purchase_url = (
        f"/api/v1/productos/{created['id']}/comprar"
    )

    first_purchase = client.patch(
        purchase_url,
        json={"precio_unitario_real": "20.00"},
    )

    assert first_purchase.status_code == 200

    second_purchase = client.patch(
        purchase_url,
        json={"precio_unitario_real": "22.00"},
    )

    assert second_purchase.status_code == 409
    assert second_purchase.json()["error"]["codigo"] == (
        "PRODUCTO_YA_COMPRADO"
    )

    delete_response = client.delete(
        f"/api/v1/productos/{created['id']}"
    )

    assert delete_response.status_code == 409
    assert delete_response.json()["error"]["codigo"] == (
        "PRODUCTO_YA_COMPRADO"
    )


def test_correct_purchased_product(api_context):
    client, year = api_context
    created = create_product(client, year)

    client.patch(
        f"/api/v1/productos/{created['id']}/comprar",
        json={"precio_unitario_real": "20.00"},
    )

    response = client.patch(
        f"/api/v1/productos/{created['id']}/correccion-compra",
        json=product_payload(
            nombre="Producto corregido",
            cantidad="4",
            precio_unitario_estimado="28.00",
            precio_unitario_real="24.00",
        ),
    )

    assert response.status_code == 200

    corrected = response.json()

    assert corrected["id"] == created["id"]
    assert corrected["nombre"] == "Producto corregido"
    assert corrected["estado"] == "comprado"
    assert corrected["precio_unitario_real"] == "24.00"


def test_correction_requires_purchased_product(api_context):
    client, year = api_context
    created = create_product(client, year)

    response = client.patch(
        f"/api/v1/productos/{created['id']}/correccion-compra",
        json=product_payload(
            precio_unitario_real="20.00"
        ),
    )

    assert response.status_code == 409
    assert response.json()["error"]["codigo"] == (
        "PRODUCTO_NO_COMPRADO"
    )


def test_invalid_product_returns_uniform_error(api_context):
    client, year = api_context

    response = client.get(
        "/api/v1/productos/identificador-invalido"
    )

    assert response.status_code == 404
    assert response.json()["error"]["codigo"] == (
        "PRODUCTO_NO_ENCONTRADO"
    )

    assert set(response.json()["error"]) == {
        "codigo",
        "mensaje",
        "detalles",
    }


def test_invalid_quantity_is_rejected(api_context):
    client, year = api_context

    response = client.post(
        f"/api/v1/anios/{year}/celebraciones/navidad/productos",
        json=product_payload(cantidad="0"),
    )

    assert response.status_code == 422
    assert response.json()["error"]["codigo"] == "DATOS_INVALIDOS"


def test_invalid_celebration_is_rejected(api_context):
    client, year = api_context

    response = client.get(
        f"/api/v1/anios/{year}/celebraciones/otra/productos"
    )

    assert response.status_code == 422
