
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.models.entities import (
    Anio,
    CategoriaProducto,
    Celebracion,
    EstadoProducto,
    Producto,
    TipoCelebracion,
    UnidadProducto,
)
from app.services.report_service import ReportService



def crear_producto(
    nombre="Producto de prueba",
    cantidad="2.50",
    precio_estimado="18000.50",
    estado=EstadoProducto.PENDIENTE,
    precio_real=None,
):
    """Construye un producto válido para las pruebas."""
    ahora = datetime.now(timezone.utc)

    if estado == EstadoProducto.COMPRADO and precio_real is None:
        precio_real = "20000.00"

    return Producto(
        id=uuid4(),
        nombre=nombre,
        categoria=CategoriaProducto.ALIMENTOS,
        cantidad=Decimal(cantidad),
        unidad=UnidadProducto.KILOGRAMO,
        precio_unitario_estimado=Decimal(precio_estimado),
        precio_unitario_real=(
            Decimal(precio_real) if precio_real is not None else None
        ),
        estado=estado,
        fecha_creacion=ahora,
        fecha_actualizacion=ahora,
    )

def crear_anio(
    presupuesto_general="2000000.00",
    presupuesto_navidad="1200000.00",
    presupuesto_fin_anio="800000.00",
    productos_navidad=None,
    productos_fin_anio=None,
):
    """Construye un año válido con sus dos celebraciones."""
    ahora = datetime.now(timezone.utc)

    navidad = Celebracion(
        id=uuid4(),
        tipo=TipoCelebracion.NAVIDAD,
        presupuesto=(
            Decimal(presupuesto_navidad)
            if presupuesto_navidad is not None
            else None
        ),
        productos=productos_navidad or [],
    )

    fin_anio = Celebracion(
        id=uuid4(),
        tipo=TipoCelebracion.FIN_DE_ANIO,
        presupuesto=(
            Decimal(presupuesto_fin_anio)
            if presupuesto_fin_anio is not None
            else None
        ),
        productos=productos_fin_anio or [],
    )

    return Anio(
        id=uuid4(),
        anio=2027,
        presupuesto_general=(
            Decimal(presupuesto_general)
            if presupuesto_general is not None
            else None
        ),
        fecha_creacion=ahora,
        fecha_actualizacion=ahora,
        celebraciones=[navidad, fin_anio],
    )


# ---------------------------------------------------------
# CÁLCULO DE COSTOS ESTIMADOS
# ---------------------------------------------------------

def test_costo_estimado_producto_usa_precision_decimal():
    producto = crear_producto(
        cantidad="2.50",
        precio_estimado="18000.50",
    )

    resultado = ReportService.costo_estimado_producto(producto)

    assert resultado == Decimal("45001.2500")


def test_gasto_estimado_incluye_productos_pendientes():
    productos = [
        crear_producto(
            cantidad="2",
            precio_estimado="10000",
        ),
        crear_producto(
            cantidad="3",
            precio_estimado="5000",
        ),
    ]

    anio = crear_anio(productos_navidad=productos)

    resultado = ReportService.gasto_estimado_celebracion(
        anio.celebraciones[0]
    )

    assert resultado == Decimal("35000")


def test_gasto_estimado_no_incluye_productos_comprados():
    productos = [
        crear_producto(
            cantidad="2",
            precio_estimado="10000",
        ),
        crear_producto(
            cantidad="3",
            precio_estimado="5000",
            estado=EstadoProducto.COMPRADO,
            precio_real="6000",
        ),
    ]

    anio = crear_anio(productos_navidad=productos)

    resultado = ReportService.gasto_estimado_celebracion(
        anio.celebraciones[0]
    )

    assert resultado == Decimal("20000")


def test_gasto_estimado_general_suma_las_dos_celebraciones():
    anio = crear_anio(
        productos_navidad=[
            crear_producto(cantidad="2", precio_estimado="10000")
        ],
        productos_fin_anio=[
            crear_producto(cantidad="3", precio_estimado="5000")
        ],
    )

    resultado = ReportService.gasto_estimado_general(anio)

    assert resultado == Decimal("35000")


def test_calcular_gasto_estimado_no_modifica_gasto_real():
    producto = crear_producto(
        cantidad="2.50",
        precio_estimado="18000.50",
    )

    anio = crear_anio(productos_navidad=[producto])

    gasto_real_antes = ReportService.dashboard(anio)["gasto_real_general"]

    ReportService.gasto_estimado_general(anio)

    gasto_real_despues = ReportService.dashboard(anio)["gasto_real_general"]

    assert gasto_real_antes == "0.00"
    assert gasto_real_despues == "0.00"


# ---------------------------------------------------------
# ALERTAS DINÁMICAS
# ---------------------------------------------------------

def test_genera_alerta_al_alcanzar_el_80_por_ciento():
    producto = crear_producto(
        cantidad="8",
        precio_estimado="100",
        estado=EstadoProducto.COMPRADO,
        precio_real="100",
    )

    anio = crear_anio(
        presupuesto_navidad="1000",
        productos_navidad=[producto],
    )

    alertas = ReportService.generar_alertas(anio)

    alerta = next(
        alerta
        for alerta in alertas
        if alerta["codigo"] == "PRESUPUESTO_80"
        and alerta["alcance"] == "navidad"
    )

    assert alerta["tipo"] == "preventiva"
    assert alerta["porcentaje_consumido"] == "80.00"


def test_genera_alerta_al_superar_el_80_por_ciento():
    producto = crear_producto(
        cantidad="9",
        precio_estimado="100",
        estado=EstadoProducto.COMPRADO,
        precio_real="100",
    )

    anio = crear_anio(
        presupuesto_navidad="1000",
        productos_navidad=[producto],
    )

    alertas = ReportService.generar_alertas(anio)

    assert any(
        alerta["codigo"] == "PRESUPUESTO_80"
        and alerta["alcance"] == "navidad"
        for alerta in alertas
    )


def test_genera_alerta_de_presupuesto_excedido():
    producto = crear_producto(
        cantidad="11",
        precio_estimado="100",
        estado=EstadoProducto.COMPRADO,
        precio_real="100",
    )

    anio = crear_anio(
        presupuesto_navidad="1000",
        productos_navidad=[producto],
    )

    alertas = ReportService.generar_alertas(anio)

    assert any(
        alerta["codigo"] == "PRESUPUESTO_EXCEDIDO"
        and alerta["alcance"] == "navidad"
        for alerta in alertas
    )


def test_genera_alerta_de_asignacion_superior_al_presupuesto_general():
    anio = crear_anio(
        presupuesto_general="1000000",
        presupuesto_navidad="1200000",
    )

    alertas = ReportService.generar_alertas(anio)

    assert any(
        alerta["codigo"] == "ASIGNACION_SUPERIOR_GENERAL"
        and alerta["alcance"] == "navidad"
        for alerta in alertas
    )


def test_no_genera_alertas_si_no_hay_presupuestos():
    anio = crear_anio(
        presupuesto_general=None,
        presupuesto_navidad=None,
        presupuesto_fin_anio=None,
    )

    alertas = ReportService.generar_alertas(anio)

    assert alertas == []


def test_alertas_se_calculan_dinamicamente():
    anio = crear_anio(
        presupuesto_navidad="1000",
        productos_navidad=[
            crear_producto(
                cantidad="8",
                precio_estimado="100",
                estado=EstadoProducto.COMPRADO,
                precio_real="100",
            )
        ],
    )

    alertas_primera_consulta = ReportService.generar_alertas(anio)
    alertas_segunda_consulta = ReportService.generar_alertas(anio)

    assert alertas_primera_consulta == alertas_segunda_consulta


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

def test_dashboard_devuelve_estructura_esperada():
    anio = crear_anio(
        productos_navidad=[
            crear_producto(
                cantidad="2",
                precio_estimado="100",
                estado=EstadoProducto.COMPRADO,
                precio_real="125",
            ),
            crear_producto(
                cantidad="3",
                precio_estimado="100",
            ),
        ]
    )

    resultado = ReportService.dashboard(anio)

    assert resultado["anio"] == 2027
    assert resultado["presupuesto_general"] == "2000000.00"
    assert resultado["gasto_real_general"] == "250.00"
    assert resultado["gasto_estimado_general"] == "300.00"

    navidad = resultado["celebraciones"]["navidad"]

    assert navidad["productos_comprados"] == 1
    assert navidad["productos_pendientes"] == 1
    assert navidad["gasto_real"] == "250.00"
    assert navidad["gasto_estimado"] == "300.00"
    assert navidad["avance_compras"] == "50.00"


def test_dashboard_representa_presupuesto_no_configurado():
    anio = crear_anio(
        presupuesto_general=None,
        presupuesto_navidad=None,
        presupuesto_fin_anio=None,
    )

    resultado = ReportService.dashboard(anio)

    assert resultado["presupuesto_general"] is None
    assert resultado["gasto_real_general"] == "0.00"
    assert resultado["saldo_general"] is None
    assert resultado["gasto_estimado_general"] == "0.00"


def test_dashboard_incluye_lista_de_alertas():
    anio = crear_anio()

    resultado = ReportService.dashboard(anio)

    assert "alertas" in resultado
    assert isinstance(resultado["alertas"], list)

def test_resumen_anual_consolida_presupuesto_y_gasto_por_celebracion():
    anio = crear_anio(
        productos_navidad=[
            crear_producto(
                cantidad="2",
                estado=EstadoProducto.COMPRADO,
                precio_real="100",
            )
        ],
        productos_fin_anio=[
            crear_producto(
                cantidad="1",
                estado=EstadoProducto.COMPRADO,
                precio_real="80",
            )
        ],
    )

    resultado = ReportService.resumen_anual(anio)

    assert resultado["anio"] == 2027

    assert resultado["celebraciones"]["navidad"] == {
        "presupuesto": "1200000.00",
        "gasto_real": "200.00",
        "saldo": "1199800.00",
    }

    assert resultado["celebraciones"]["fin_anio"] == {
        "presupuesto": "800000.00",
        "gasto_real": "80.00",
        "saldo": "799920.00",
    }

def test_resumen_anual_representa_presupuestos_no_configurados():
    anio = crear_anio(
        presupuesto_general=None,
        presupuesto_navidad=None,
        presupuesto_fin_anio=None,
    )

    resultado = ReportService.resumen_anual(anio)

    for celebracion in resultado["celebraciones"].values():
        assert celebracion["presupuesto"] is None
        assert celebracion["gasto_real"] == "0.00"
        assert celebracion["saldo"] is None