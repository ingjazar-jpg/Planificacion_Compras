
import json
from decimal import Decimal

import pytest

from app.models.entities import (
    Anio,
    Celebracion,
    DatosCompras,
    Metadata,
)
from app.repositories.json_repository import JsonRepository


def crear_documento():
    anio = Anio(
        id="550e8400-e29b-41d4-a716-446655440000",
        anio=2026,
        presupuesto_general=Decimal("1500000.50"),
        fecha_creacion="2026-11-12T10:00:00",
        fecha_actualizacion="2026-11-12T10:00:00",
        celebraciones=[
            Celebracion(
                id="550e8400-e29b-41d4-a716-446655440001",
                tipo="Navidad",
                presupuesto=Decimal("750000.25"),
                productos=[],
            ),
            Celebracion(
                id="550e8400-e29b-41d4-a716-446655440002",
                tipo="Fin de Año",
                presupuesto=Decimal("750000.25"),
                productos=[],
            ),
        ],
    )

    return DatosCompras(
        metadata=Metadata(schema_version="1.0"),
        anios=[anio],
    )


def test_load_crea_documento_inicial_si_no_existe(tmp_path):
    ruta = tmp_path / "datos_compras.json"
    repositorio = JsonRepository(ruta)

    documento = repositorio.load()

    assert ruta.exists()
    assert documento.metadata.schema_version == "1.0"
    assert documento.anios == []


def test_save_y_load_conservan_los_datos(tmp_path):
    ruta = tmp_path / "datos_compras.json"
    repositorio = JsonRepository(ruta)

    original = crear_documento()
    repositorio.save(original)

    recuperado = repositorio.load()

    assert recuperado.anios[0].anio == 2026
    assert (
        recuperado.anios[0].presupuesto_general
        == Decimal("1500000.50")
    )


def test_json_conserva_precision_decimal(tmp_path):
    ruta = tmp_path / "datos_compras.json"
    repositorio = JsonRepository(ruta)

    repositorio.save(crear_documento())

    contenido = json.loads(ruta.read_text(encoding="utf-8"))

    assert (
        contenido["anios"][0]["presupuesto_general"]
        == "1500000.50"
    )


def test_load_rechaza_json_corrupto(tmp_path):
    ruta = tmp_path / "datos_compras.json"
    ruta.write_text("{ JSON inválido", encoding="utf-8")

    repositorio = JsonRepository(ruta)

    with pytest.raises(ValueError, match="archivo de datos no es válido"):
        repositorio.load()


def test_save_no_deja_archivos_temporales(tmp_path):
    ruta = tmp_path / "datos_compras.json"
    repositorio = JsonRepository(ruta)

    repositorio.save(crear_documento())

    temporales = list(tmp_path.glob("*.tmp"))
    assert temporales == []