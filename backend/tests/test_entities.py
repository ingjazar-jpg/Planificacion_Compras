
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.entities import (
    Anio,
    Celebracion,
    DatosCompras,
    EstadoProducto,
    Metadata,
    Producto,
)


# ============================================================
# DATOS DE PRUEBA
# ============================================================

FECHA = datetime(2026, 11, 12, 10, 0, 0)


def crear_producto(
    estado="pendiente",
    precio_real=None,
):
    return Producto(
        id=uuid4(),
        nombre="Producto de prueba",
        descripcion=None,
        categoria="Alimentos",
        cantidad=Decimal("2"),
        unidad="Kilogramo",
        precio_unitario_estimado=Decimal("10.50"),
        precio_unitario_real=precio_real,
        estado=estado,
        fecha_creacion=FECHA,
        fecha_actualizacion=FECHA,
    )


def crear_anio(numero=2026, presupuesto=Decimal("1000")):
    return Anio(
        id=uuid4(),
        anio=numero,
        presupuesto_general=presupuesto,
        fecha_creacion=FECHA,
        fecha_actualizacion=FECHA,
        celebraciones=[
            Celebracion(
                id=uuid4(),
                tipo="Navidad",
                presupuesto=Decimal("500"),
                productos=[],
            ),
            Celebracion(
                id=uuid4(),
                tipo="Fin de Año",
                presupuesto=Decimal("500"),
                productos=[],
            ),
        ],
    )


def crear_documento(anios):
    return DatosCompras(
        metadata=Metadata(schema_version="1.0"),
        anios=anios,
    )


# ============================================================
# PRUEBAS DE PRODUCTO
# ============================================================

def test_producto_pendiente_sin_precio_real():
    producto = crear_producto()

    assert producto.estado == EstadoProducto.PENDIENTE
    assert producto.precio_unitario_real is None


def test_producto_comprado_con_precio_real():
    producto = crear_producto(
        estado="comprado",
        precio_real=Decimal("12.50"),
    )

    assert producto.estado == EstadoProducto.COMPRADO
    assert producto.precio_unitario_real == Decimal("12.50")


def test_producto_comprado_admite_precio_real_cero():
    producto = crear_producto(
        estado="comprado",
        precio_real=Decimal("0"),
    )

    assert producto.precio_unitario_real == Decimal("0")


def test_producto_pendiente_no_admite_precio_real():
    with pytest.raises(ValidationError):
        crear_producto(
            estado="pendiente",
            precio_real=Decimal("12.50"),
        )


def test_producto_comprado_requiere_precio_real():
    with pytest.raises(ValidationError):
        crear_producto(estado="comprado")


def test_producto_no_admite_cantidad_cero():
    with pytest.raises(ValidationError):
        Producto(
            id=uuid4(),
            nombre="Producto inválido",
            categoria="Alimentos",
            cantidad=Decimal("0"),
            unidad="Unidad",
            precio_unitario_estimado=Decimal("10"),
            precio_unitario_real=None,
            estado="pendiente",
            fecha_creacion=FECHA,
            fecha_actualizacion=FECHA,
        )


# ============================================================
# PRUEBAS DE PRESUPUESTOS
# ============================================================

def test_presupuesto_general_cero_se_normaliza_a_none():
    anio = crear_anio(presupuesto=Decimal("0"))

    assert anio.presupuesto_general is None


def test_presupuesto_de_celebracion_cero_se_normaliza_a_none():
    celebracion = Celebracion(
        id=uuid4(),
        tipo="Navidad",
        presupuesto=Decimal("0"),
        productos=[],
    )

    assert celebracion.presupuesto is None


def test_presupuesto_negativo_no_es_admitido():
    with pytest.raises(ValidationError):
        crear_anio(presupuesto=Decimal("-100"))


# ============================================================
# PRUEBAS DE CELEBRACIONES
# ============================================================

def test_anio_requiere_navidad_y_fin_de_anio():
    anio = crear_anio()

    tipos = {celebracion.tipo.value for celebracion in anio.celebraciones}

    assert tipos == {"Navidad", "Fin de Año"}
    assert len(anio.celebraciones) == 2


def test_anio_no_admite_celebraciones_duplicadas():
    with pytest.raises(ValidationError):
        Anio(
            id=uuid4(),
            anio=2026,
            presupuesto_general=None,
            fecha_creacion=FECHA,
            fecha_actualizacion=FECHA,
            celebraciones=[
                Celebracion(
                    id=uuid4(),
                    tipo="Navidad",
                    productos=[],
                ),
                Celebracion(
                    id=uuid4(),
                    tipo="Navidad",
                    productos=[],
                ),
            ],
        )


def test_anio_no_admite_una_sola_celebracion():
    with pytest.raises(ValidationError):
        Anio(
            id=uuid4(),
            anio=2026,
            presupuesto_general=None,
            fecha_creacion=FECHA,
            fecha_actualizacion=FECHA,
            celebraciones=[
                Celebracion(
                    id=uuid4(),
                    tipo="Navidad",
                    productos=[],
                ),
            ],
        )


# ============================================================
# PRUEBAS DEL DOCUMENTO PRINCIPAL
# ============================================================

def test_documento_admite_anios_diferentes():
    documento = crear_documento([
        crear_anio(2026),
        crear_anio(2027),
    ])

    assert len(documento.anios) == 2


def test_documento_no_admite_anios_duplicados():
    with pytest.raises(ValidationError):
        crear_documento([
            crear_anio(2026),
            crear_anio(2026),
        ])


def test_documento_requiere_version_de_esquema_valida():
    with pytest.raises(ValidationError):
        Metadata(schema_version="2.0")
