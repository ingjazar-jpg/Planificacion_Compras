
from decimal import Decimal

from app.models.entities import (
    Anio,
    Celebracion,
    EstadoProducto,
)


CERO = Decimal("0")


def gasto_real_celebracion(celebracion: Celebracion) -> Decimal:
    """
    Calcula el gasto real de una celebración.

    Solo incluye productos comprados y utiliza el precio real.
    """

    return sum(
        (
            producto.cantidad * producto.precio_unitario_real
            for producto in celebracion.productos
            if (
                producto.estado == EstadoProducto.COMPRADO
                and producto.precio_unitario_real is not None
            )
        ),
        start=CERO,
    )


def gasto_real_general(anio: Anio) -> Decimal:
    """Suma el gasto real de Navidad y Fin de Año."""

    return sum(
        (
            gasto_real_celebracion(celebracion)
            for celebracion in anio.celebraciones
        ),
        start=CERO,
    )


def saldo_presupuesto(
    presupuesto: Decimal | None,
    gasto_real: Decimal,
) -> Decimal | None:
    """
    Calcula el saldo usando exclusivamente el gasto real.

    Si no existe presupuesto configurado, devuelve None.
    """

    if presupuesto is None:
        return None

    return presupuesto - gasto_real


def presupuesto_excedido(
    presupuesto: Decimal | None,
    gasto_real: Decimal,
) -> bool:
    """
    Indica si el gasto real supera el presupuesto.

    No genera alerta cuando el gasto es igual al presupuesto
    ni cuando no existe presupuesto configurado.
    """

    if presupuesto is None:
        return False

    return gasto_real > presupuesto


def avance_compras(celebracion: Celebracion) -> Decimal:
    """
    Calcula el porcentaje de productos comprados.

    Fórmula:
        productos comprados / productos registrados * 100

    Si no hay productos, devuelve cero.
    """

    total = len(celebracion.productos)

    if total == 0:
        return CERO

    comprados = sum(
        1
        for producto in celebracion.productos
        if producto.estado == EstadoProducto.COMPRADO
    )

    return Decimal(comprados) / Decimal(total) * Decimal("100")


def indicadores_celebracion(celebracion: Celebracion) -> dict:
    """Obtiene los indicadores derivados de una celebración."""

    gasto_real = gasto_real_celebracion(celebracion)

    return {
        "gasto_real": gasto_real,
        "saldo": saldo_presupuesto(
            celebracion.presupuesto,
            gasto_real,
        ),
        "presupuesto_excedido": presupuesto_excedido(
            celebracion.presupuesto,
            gasto_real,
        ),
        "avance": avance_compras(celebracion),
    }


def indicadores_anio(anio: Anio) -> dict:
    """Obtiene los indicadores generales y por celebración."""

    gasto_real = gasto_real_general(anio)

    return {
        "gasto_real": gasto_real,
        "saldo": saldo_presupuesto(
            anio.presupuesto_general,
            gasto_real,
        ),
        "presupuesto_excedido": presupuesto_excedido(
            anio.presupuesto_general,
            gasto_real,
        ),
        "celebraciones": {
            celebracion.tipo.value: indicadores_celebracion(celebracion)
            for celebracion in anio.celebraciones
        },
    }
