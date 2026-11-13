
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_year_service
from app.models.entities import (
    Anio,
    CategoriaProducto,
    Celebracion,
    EstadoProducto,
    Producto,
    TipoCelebracion,
    UnidadProducto,
)
from app.services.year_service import YearNotFoundError


client = TestClient(app)


class FakeYearService:
    """Servicio simulado para probar los endpoints sin tocar el JSON."""

    def __init__(self, anio=None, error=None):
        self.anio = anio
        self.error = error

    def get_year(self, year):
        if self.error:
            raise self.error

        return self.anio


def crear_producto(
    nombre,
    categoria,
    cantidad,
    precio_estimado,
    estado=EstadoProducto.PENDIENTE,
    precio_real=None,
):
    """Construye un producto válido para las pruebas."""

    ahora = datetime.now()

    return Producto(
        id=uuid4(),
        nombre=nombre,
        descripcion=None,
        categoria=categoria,
        cantidad=Decimal(cantidad),
        unidad=UnidadProducto.UNIDAD,
        precio_unitario_estimado=Decimal(precio_estimado),
        precio_unitario_real=(
            Decimal(precio_real) if precio_real is not None else None
        ),
        estado=estado,
        fecha_creacion=ahora,
        fecha_actualizacion=ahora,
    )


def crear_anio_prueba():
    ahora = datetime.now()

    navidad = Celebracion(
        id=uuid4(),
        tipo=TipoCelebracion.NAVIDAD,
        presupuesto=Decimal("1000000.00"),
        productos=[],
    )

    fin_anio = Celebracion(
        id=uuid4(),
        tipo=TipoCelebracion.FIN_DE_ANIO,
        presupuesto=Decimal("500000.00"),
        productos=[],
    )

    return Anio(
        id=uuid4(),
        anio=2027,
        presupuesto_general=Decimal("1500000.00"),
        fecha_creacion=ahora,
        fecha_actualizacion=ahora,
        celebraciones=[navidad, fin_anio],
    )


def crear_anio_con_productos():
    """Construye un año con productos comprados y pendientes."""

    anio = crear_anio_prueba()

    navidad = next(
        c for c in anio.celebraciones
        if c.tipo == TipoCelebracion.NAVIDAD
    )

    fin_anio = next(
        c for c in anio.celebraciones
        if c.tipo == TipoCelebracion.FIN_DE_ANIO
    )

    navidad.productos = [
        crear_producto(
            nombre="Arroz",
            categoria=CategoriaProducto.ALIMENTOS,
            cantidad="2",
            precio_estimado="120",
            estado=EstadoProducto.COMPRADO,
            precio_real="100",
        ),
        crear_producto(
            nombre="Carne",
            categoria=CategoriaProducto.ALIMENTOS,
            cantidad="3",
            precio_estimado="50",
        ),
        crear_producto(
            nombre="Bebida",
            categoria=CategoriaProducto.BEBIDAS,
            cantidad="2",
            precio_estimado="30",
        ),
    ]

    fin_anio.productos = [
        crear_producto(
            nombre="Refresco",
            categoria=CategoriaProducto.BEBIDAS,
            cantidad="1",
            precio_estimado="40",
            estado=EstadoProducto.COMPRADO,
            precio_real="80",
        ),
    ]

    return anio


def configurar_servicio(anio=None, error=None):
    app.dependency_overrides[get_year_service] = (
        lambda: FakeYearService(anio=anio, error=error)
    )


def test_dashboard_devuelve_respuesta_correcta():
    configurar_servicio(anio=crear_anio_prueba())

    try:
        response = client.get("/api/v1/anios/2027/dashboard")

        assert response.status_code == 200

        datos = response.json()

        assert datos["anio"] == 2027
        assert datos["presupuesto_general"] == "1500000.00"
        assert datos["gasto_real_general"] == "0.00"
        assert datos["gasto_estimado_general"] == "0.00"
        assert "navidad" in datos["celebraciones"]
        assert "fin_anio" in datos["celebraciones"]
        assert isinstance(datos["alertas"], list)

    finally:
        app.dependency_overrides.clear()


def test_dashboard_devuelve_error_si_anio_no_existe():
    configurar_servicio(
        error=YearNotFoundError("No existe el año.")
    )

    try:
        response = client.get("/api/v1/anios/2027/dashboard")

        assert response.status_code == 404

        assert response.json() == {
            "error": {
                "codigo": "ANIO_NO_ENCONTRADO",
                "mensaje": "No existe el año.",
                "detalles": [],
            }
        }

    finally:
        app.dependency_overrides.clear()


def test_dashboard_rechaza_anio_con_formato_invalido():
    response = client.get("/api/v1/anios/no-valido/dashboard")

    assert response.status_code == 422


def test_dashboard_aparece_en_openapi():
    schema = client.get("/openapi.json").json()

    assert "/api/v1/anios/{anio}/dashboard" in schema["paths"]


def test_resumen_navidad_devuelve_indicadores_correctos():
    anio = crear_anio_con_productos()
    configurar_servicio(anio=anio)

    try:
        response = client.get(
            "/api/v1/anios/2027/celebraciones/navidad/resumen"
        )

        assert response.status_code == 200

        datos = response.json()

        assert datos["anio"] == 2027
        assert datos["tipo"] == "navidad"
        assert datos["presupuesto"] == "1000000.00"
        assert datos["gasto_real"] == "200.00"
        assert datos["saldo"] == "999800.00"
        assert datos["gasto_estimado"] == "210.00"
        assert datos["productos_comprados"] == 1
        assert datos["productos_pendientes"] == 2
        assert datos["avance_compras"] == "33.33"
        assert isinstance(datos["alertas"], list)

    finally:
        app.dependency_overrides.clear()


def test_resumen_fin_anio_devuelve_indicadores_correctos():
    anio = crear_anio_con_productos()
    configurar_servicio(anio=anio)

    try:
        response = client.get(
            "/api/v1/anios/2027/celebraciones/fin_anio/resumen"
        )

        assert response.status_code == 200

        datos = response.json()

        assert datos["tipo"] == "fin_anio"
        assert datos["gasto_real"] == "80.00"
        assert datos["productos_comprados"] == 1
        assert datos["productos_pendientes"] == 0
        assert datos["avance_compras"] == "100.00"

    finally:
        app.dependency_overrides.clear()


def test_resumen_rechaza_tipo_invalido():
    response = client.get(
        "/api/v1/anios/2027/celebraciones/otra/resumen"
    )

    assert response.status_code == 422


def test_resumen_devuelve_error_si_anio_no_existe():
    configurar_servicio(
        error=YearNotFoundError("No existe el año.")
    )

    try:
        response = client.get(
            "/api/v1/anios/2027/celebraciones/navidad/resumen"
        )

        assert response.status_code == 404
        assert response.json()["error"]["codigo"] == "ANIO_NO_ENCONTRADO"

    finally:
        app.dependency_overrides.clear()


def test_estadisticas_categorias_devuelve_distribucion_correcta():
    anio = crear_anio_con_productos()
    configurar_servicio(anio=anio)

    try:
        response = client.get(
            "/api/v1/anios/2027/estadisticas/categorias"
        )

        assert response.status_code == 200

        datos = response.json()

        assert datos["anio"] == 2027
        assert datos["gasto_real_general"] == "280.00"

        categorias = {
            item["categoria"]: item
            for item in datos["categorias"]
        }

        alimentos = categorias["Alimentos"]
        assert alimentos["productos_total"] == 2
        assert alimentos["productos_comprados"] == 1
        assert alimentos["productos_pendientes"] == 1
        assert alimentos["gasto_real"] == "200.00"
        assert alimentos["gasto_estimado"] == "150.00"
        assert alimentos["participacion_porcentual"] == "71.43"

        bebidas = categorias["Bebidas"]
        assert bebidas["productos_total"] == 2
        assert bebidas["productos_comprados"] == 1
        assert bebidas["productos_pendientes"] == 1
        assert bebidas["gasto_real"] == "80.00"
        assert bebidas["gasto_estimado"] == "60.00"
        assert bebidas["participacion_porcentual"] == "28.57"

        assert len(datos["categorias"]) == len(CategoriaProducto)

        assert categorias["Otros"]["productos_total"] == 0
        assert categorias["Otros"]["participacion_porcentual"] == "0.00"

    finally:
        app.dependency_overrides.clear()


def test_estadisticas_categorias_sin_gasto_real_devuelven_cero():
    anio = crear_anio_prueba()
    configurar_servicio(anio=anio)

    try:
        response = client.get(
            "/api/v1/anios/2027/estadisticas/categorias"
        )

        assert response.status_code == 200

        datos = response.json()

        assert datos["gasto_real_general"] == "0.00"

        for categoria in datos["categorias"]:
            assert categoria["participacion_porcentual"] == "0.00"

    finally:
        app.dependency_overrides.clear()


def test_estadisticas_categorias_devuelve_error_si_anio_no_existe():
    configurar_servicio(
        error=YearNotFoundError("No existe el año.")
    )

    try:
        response = client.get(
            "/api/v1/anios/2027/estadisticas/categorias"
        )

        assert response.status_code == 404
        assert response.json()["error"]["codigo"] == "ANIO_NO_ENCONTRADO"

    finally:
        app.dependency_overrides.clear()


def test_nuevos_reportes_aparecen_en_openapi():
    schema = client.get("/openapi.json").json()

    assert (
        "/api/v1/anios/{anio}/celebraciones/{tipo}/resumen"
        in schema["paths"]
    )

    assert (
        "/api/v1/anios/{anio}/estadisticas/categorias"
        in schema["paths"]
    )
