
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_consultar_catalogos_devuelve_estructura_completa():
    response = client.get("/api/v1/catalogos")

    assert response.status_code == 200

    datos = response.json()

    assert set(datos) == {
        "categorias",
        "unidades",
        "estados",
    }

    assert len(datos["categorias"]) == 6
    assert len(datos["unidades"]) == 9
    assert len(datos["estados"]) == 2


def test_catalogos_conservan_valores_y_orden_aprobados():
    response = client.get("/api/v1/catalogos")

    datos = response.json()

    assert datos["categorias"] == [
        {"valor": "alimentos", "etiqueta": "Alimentos"},
        {"valor": "bebidas", "etiqueta": "Bebidas"},
        {"valor": "ingredientes", "etiqueta": "Ingredientes"},
        {"valor": "decoracion", "etiqueta": "Decoración"},
        {
            "valor": "desechables_utensilios",
            "etiqueta": "Desechables y utensilios",
        },
        {"valor": "otros", "etiqueta": "Otros"},
    ]

    assert datos["unidades"] == [
        {"valor": "unidad", "etiqueta": "Unidad"},
        {"valor": "kilogramo", "etiqueta": "Kilogramo"},
        {"valor": "gramo", "etiqueta": "Gramo"},
        {"valor": "litro", "etiqueta": "Litro"},
        {"valor": "mililitro", "etiqueta": "Mililitro"},
        {"valor": "paquete", "etiqueta": "Paquete"},
        {"valor": "botella", "etiqueta": "Botella"},
        {"valor": "docena", "etiqueta": "Docena"},
        {"valor": "otro", "etiqueta": "Otro"},
    ]

    assert datos["estados"] == [
        {"valor": "pendiente", "etiqueta": "Pendiente"},
        {"valor": "comprado", "etiqueta": "Comprado"},
    ]


def test_catalogos_aparece_en_openapi():
    schema = client.get("/openapi.json").json()

    assert "/api/v1/catalogos" in schema["paths"]
