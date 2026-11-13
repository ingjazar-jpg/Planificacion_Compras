
from pydantic import BaseModel, ConfigDict


class ReportResponseBase(BaseModel):
    """Configuración común para las respuestas de reportes."""

    model_config = ConfigDict(extra="forbid")


class AlertaResponse(ReportResponseBase):
    """Estructura de una alerta generada por el sistema."""

    codigo: str
    tipo: str | None = None
    alcance: str
    mensaje: str
    porcentaje_consumido: str | None = None


class CelebracionDashboardResponse(ReportResponseBase):
    """Indicadores de una celebración en el dashboard."""

    presupuesto: str | None
    gasto_real: str | None
    saldo: str | None
    gasto_estimado: str
    productos_comprados: int
    productos_pendientes: int
    avance_compras: str


class DashboardResponse(ReportResponseBase):
    """Respuesta del dashboard general."""

    anio: int
    presupuesto_general: str | None
    gasto_real_general: str
    saldo_general: str | None
    gasto_estimado_general: str
    celebraciones: dict[str, CelebracionDashboardResponse]
    alertas: list[AlertaResponse]

class ResumenAnualCelebracionResponse(ReportResponseBase):
    """Presupuesto y gasto real de una celebración."""

    presupuesto: str | None
    gasto_real: str
    saldo: str | None


class ResumenAnualResponse(ReportResponseBase):
    """Resumen anual de Navidad y Fin de Año."""

    anio: int
    celebraciones: dict[str, ResumenAnualCelebracionResponse]

class ResumenCelebracionResponse(ReportResponseBase):
    """Resumen individual de Navidad o Fin de Año."""

    anio: int
    tipo: str
    presupuesto: str | None
    gasto_real: str
    saldo: str | None
    gasto_estimado: str
    productos_comprados: int
    productos_pendientes: int
    avance_compras: str
    alertas: list[AlertaResponse]


class CategoriaEstadisticaResponse(ReportResponseBase):
    """Indicadores de productos y gastos de una categoría."""

    categoria: str
    productos_total: int
    productos_comprados: int
    productos_pendientes: int
    gasto_real: str
    gasto_estimado: str
    participacion_porcentual: str


class EstadisticasCategoriasResponse(ReportResponseBase):
    """Distribución de productos y gastos por categoría."""

    anio: int
    gasto_real_general: str
    categorias: list[CategoriaEstadisticaResponse]
