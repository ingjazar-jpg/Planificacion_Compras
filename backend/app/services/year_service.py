
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from app.models.entities import (
    Anio,
    Celebracion,
    DatosCompras,
    TipoCelebracion,
)
from app.repositories.json_repository import JsonRepository


# ============================================================
# EXCEPCIONES DE DOMINIO
# ============================================================

class YearServiceError(Exception):
    """Error base del servicio de gestión de años."""


class YearAlreadyExistsError(YearServiceError):
    """El año ya está registrado."""


class YearNotFoundError(YearServiceError):
    """El año solicitado no existe."""


class HistoricalYearReadOnlyError(YearServiceError):
    """No se permiten modificaciones en años históricos."""


class CelebrationNotFoundError(YearServiceError):
    """La celebración solicitada no existe."""


# ============================================================
# SERVICIO DE GESTIÓN DE AÑOS
# ============================================================

class YearService:
    """
    Gestiona años y presupuestos del sistema.

    La persistencia se delega exclusivamente en JsonRepository.
    """

    def __init__(self, repository: JsonRepository | None = None):
        self.repository = repository or JsonRepository()

    # --------------------------------------------------------
    # CONSULTAS
    # --------------------------------------------------------

    def list_years(self) -> list[Anio]:
        """Devuelve todos los años registrados."""

        documento = self.repository.load()

        return sorted(
            documento.anios,
            key=lambda registro: registro.anio,
        )

    def get_year(self, year: int) -> Anio:
        """Consulta un año por su número."""

        documento = self.repository.load()

        for registro in documento.anios:
            if registro.anio == year:
                return registro

        raise YearNotFoundError(
            f"No existe un registro para el año {year}."
        )

    # --------------------------------------------------------
    # CREACIÓN
    # --------------------------------------------------------

    def create_year(
        self,
        year: int,
        general_budget: Decimal | None = None,
        christmas_budget: Decimal | None = None,
        new_year_budget: Decimal | None = None,
    ) -> Anio:
        """
        Crea un año con sus dos celebraciones obligatorias.

        Los identificadores y las fechas son generados
        automáticamente por el servicio.
        """

        if year < datetime.now().year:
            raise HistoricalYearReadOnlyError(
                "No se pueden crear registros de años históricos."
            )

        documento = self.repository.load()

        if any(registro.anio == year for registro in documento.anios):
            raise YearAlreadyExistsError(
                f"El año {year} ya está registrado."
            )

        now = datetime.now()

        christmas = Celebracion(
            id=uuid4(),
            tipo=TipoCelebracion.NAVIDAD,
            presupuesto=christmas_budget,
            productos=[],
        )

        new_year = Celebracion(
            id=uuid4(),
            tipo=TipoCelebracion.FIN_DE_ANIO,
            presupuesto=new_year_budget,
            productos=[],
        )

        registro = Anio(
            id=uuid4(),
            anio=year,
            presupuesto_general=general_budget,
            fecha_creacion=now,
            fecha_actualizacion=now,
            celebraciones=[christmas, new_year],
        )

        documento.anios.append(registro)
        self.repository.save(documento)

        return registro

    # --------------------------------------------------------
    # ACTUALIZACIÓN DE PRESUPUESTO GENERAL
    # --------------------------------------------------------

    def update_general_budget(
        self,
        year: int,
        budget: Decimal | None,
    ) -> Anio:
        """Actualiza el presupuesto general de un año."""

        documento = self.repository.load()
        registro = self._find_year(documento, year)

        self._ensure_editable(registro)

        registro.presupuesto_general = budget
        registro.fecha_actualizacion = datetime.now()

        self.repository.save(documento)

        return registro

    # --------------------------------------------------------
    # ACTUALIZACIÓN DE PRESUPUESTO DE CELEBRACIÓN
    # --------------------------------------------------------

    def update_celebration_budget(
        self,
        year: int,
        celebration_type: TipoCelebracion,
        budget: Decimal | None,
    ) -> Anio:
        """Actualiza el presupuesto de una celebración."""

        documento = self.repository.load()
        registro = self._find_year(documento, year)

        self._ensure_editable(registro)

        celebracion = next(
            (
                item
                for item in registro.celebraciones
                if item.tipo == celebration_type
            ),
            None,
        )

        if celebracion is None:
            raise CelebrationNotFoundError(
                f"No existe la celebración {celebration_type.value} "
                f"en el año {year}."
            )

        celebracion.presupuesto = budget
        registro.fecha_actualizacion = datetime.now()

        self.repository.save(documento)

        return registro

    # --------------------------------------------------------
    # MÉTODOS PRIVADOS
    # --------------------------------------------------------

    @staticmethod
    def _find_year(documento: DatosCompras, year: int) -> Anio:
        """Localiza un año dentro del documento."""

        for registro in documento.anios:
            if registro.anio == year:
                return registro

        raise YearNotFoundError(
            f"No existe un registro para el año {year}."
        )

    @staticmethod
    def _ensure_editable(registro: Anio) -> None:
        """Impide modificar años históricos."""

        if registro.anio < datetime.now().year:
            raise HistoricalYearReadOnlyError(
                f"El año {registro.anio} es histórico y solo permite "
                "consultas."
            )
