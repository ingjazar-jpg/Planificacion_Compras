
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from app.models.entities import Anio, Celebracion, Producto
from app.services.calculation_service import (
    avance_compras,
    gasto_real_celebracion,
    gasto_real_general,
    indicadores_anio,
    presupuesto_excedido,
    saldo_presupuesto,
)


FECHA = datetime(2026, 11, 12, 10, 0, 0)


def crear_producto(
    estado="pendiente",
    cantidad="2",
    precio_real=None,
):
    return Producto(
        id=uuid4(),
        nombre="Producto de prueba",
        categoria="Alimentos",
        cantidad=Decimal(cantidad),
        unidad="Kilogramo",
        precio_unitario_estimado=Decimal("10"),
        precio_unitario_real=(
            Decimal(precio_real) if precio_real is not None else None
        ),
        estado=estado,
        fecha_creacion=FECHA,
        fecha_actualizacion=FECHA,
    )


def crear_celebracion(
    tipo="Navidad",
    presupuesto=Decimal("100"),
    productos=None,
):
    return Celebracion(
        id=uuid4(),
        tipo=tipo,
        presupuesto=presupuesto,
        productos=productos or [],
    )


def crear_anio(
    presupuesto_general=Decimal("300"),
    navidad=None,
    fin_anio=None,
):
    return Anio(
        id=uuid4(),
        anio=2026,
        presupuesto_general=presupuesto_general,
        fecha_creacion=FECHA,
        fecha_actualizacion=FECHA,
        celebraciones=[
            navidad or crear_celebracion("Navidad"),
            fin_anio or crear_celebracion("Fin de Año"),
        ],
    )


def test_gasto_real_solo_incluye_productos_comprados():
    celebracion = crear_celebracion(
        productos=[
            crear_producto("comprado", "2", "15"),
            crear_producto("pendiente"),
        ]
    )

    assert gasto_real_celebracion(celebracion) == Decimal("30")


def test_gasto_real_considera_cantidad_y_precio_real():
    celebracion = crear_celebracion(
        productos=[
            crear_producto("comprado", "3", "12.50"),
        ]
    )

    assert gasto_real_celebracion(celebracion) == Decimal("37.50")


def test_gasto_real_admite_precio_cero():
    celebracion = crear_celebracion(
        productos=[
            crear_producto("comprado", "2", "0"),
        ]
    )

    assert gasto_real_celebracion(celebracion) == Decimal("0")


def test_gasto_real_general_suma_ambas_celebraciones():
    navidad = crear_celebracion(
        "Navidad",
        productos=[crear_producto("comprado", "2", "10")],
    )

    fin_anio = crear_celebracion(
        "Fin de Año",
        productos=[crear_producto("comprado", "3", "20")],
    )

    anio = crear_anio(navidad=navidad, fin_anio=fin_anio)

    assert gasto_real_general(anio) == Decimal("80")


def test_saldo_presupuesto_se_calcula_con_gasto_real():
    assert saldo_presupuesto(
        Decimal("100"),
        Decimal("35"),
    ) == Decimal("65")


def test_saldo_es_none_sin_presupuesto():
    assert saldo_presupuesto(None, Decimal("35")) is None


def test_no_hay_alerta_si_gasto_es_igual_al_presupuesto():
    assert presupuesto_excedido(
        Decimal("100"),
        Decimal("100"),
    ) is False


def test_hay_alerta_si_gasto_supera_el_presupuesto():
    assert presupuesto_excedido(
        Decimal("100"),
        Decimal("100.01"),
    ) is True


def test_no_hay_alerta_sin_presupuesto():
    assert presupuesto_excedido(None, Decimal("500")) is False


def test_avance_sin_productos_es_cero():
    celebracion = crear_celebracion(productos=[])

    assert avance_compras(celebracion) == Decimal("0")



def test_avance_se_calcula_sobre_productos_registrados():
    celebracion = crear_celebracion(
        productos=[
            crear_producto("comprado", precio_real="10"),
            crear_producto("pendiente"),
            crear_producto("comprado", precio_real="15"),
            crear_producto("pendiente"),
        ]
    )

    assert avance_compras(celebracion) == Decimal("50")

def test_indicadores_general_y_por_celebracion_son_independientes():
    navidad = crear_celebracion(
        "Navidad",
        presupuesto=Decimal("20"),
        productos=[crear_producto("comprado", "2", "15")],
    )

    fin_anio = crear_celebracion(
        "Fin de Año",
        presupuesto=Decimal("100"),
        productos=[crear_producto("comprado", "1", "10")],
    )

    anio = crear_anio(
        presupuesto_general=Decimal("50"),
        navidad=navidad,
        fin_anio=fin_anio,
    )

    resultado = indicadores_anio(anio)

    assert resultado["gasto_real"] == Decimal("40")
    assert resultado["presupuesto_excedido"] is False

    assert (
        resultado["celebraciones"]["Navidad"]["presupuesto_excedido"]
        is True
    )

    assert (
        resultado["celebraciones"]["Fin de Año"]["presupuesto_excedido"]
        is False
    )
