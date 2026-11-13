import { useEffect, useMemo, useState } from "react";
import { api } from "./services/api.js";
import { formatCurrency, formatPercent, formatYear } from "./utils/formatters.js";
import "./App.css";

const CELEBRATIONS = [
  { key: "navidad", label: "Navidad", icon: "✦" },
  { key: "fin_anio", label: "Fin de Año", icon: "◈" },
];

function MetricCard({ label, value, hint, accent = "blue" }) {
  return (
    <article className={`metric-card metric-card--${accent}`}>
      <span className="metric-card__label">{label}</span>
      <strong className="metric-card__value">{value}</strong>
      {hint && <span className="metric-card__hint">{hint}</span>}
    </article>
  );
}

function CelebrationCard({ celebration, label, icon }) {
  if (!celebration) return null;

  return (
    <article className="celebration-card">
      <div className="celebration-card__heading">
        <span className="celebration-card__icon" aria-hidden="true">{icon}</span>
        <div>
          <h3>{label}</h3>
          <p>Resumen de la celebración</p>
        </div>
      </div>
      <div className="celebration-card__grid">
        <div><span>Presupuesto</span><strong>{formatCurrency(celebration.presupuesto)}</strong></div>
        <div><span>Gasto real</span><strong>{formatCurrency(celebration.gasto_real)}</strong></div>
        <div><span>Saldo</span><strong>{formatCurrency(celebration.saldo)}</strong></div>
      </div>
      <div className="progress-heading">
        <span>Avance de compras</span>
        <strong>{formatPercent(celebration.avance_compras)}</strong>
      </div>
      <div className="progress-track" role="progressbar" aria-valuenow={Number(celebration.avance_compras) || 0} aria-valuemin="0" aria-valuemax="100">
        <span style={{ width: `${Math.min(100, Math.max(0, Number(celebration.avance_compras) || 0))}%` }} />
      </div>
      <div className="celebration-card__counts">
        <span>{celebration.productos_comprados ?? 0} comprados</span>
        <span>{celebration.productos_pendientes ?? 0} pendientes</span>
      </div>
    </article>
  );
}

export default function App() {
  const [years, setYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [loadingYears, setLoadingYears] = useState(true);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    api.listYears()
      .then((data) => {
        if (!active) return;
        const availableYears = data?.anios ?? [];
        setYears(availableYears);
        if (availableYears.length) {
          setSelectedYear(String(availableYears[0].anio));
        }
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setLoadingYears(false));
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!selectedYear) {
      setDashboard(null);
      return undefined;
    }
    let active = true;
    setLoadingDashboard(true);
    setError("");
    api.getDashboard(selectedYear)
      .then((data) => active && setDashboard(data))
      .catch((err) => active && setError(err.message))
      .finally(() => active && setLoadingDashboard(false));
    return () => { active = false; };
  }, [selectedYear]);

  const celebrationCards = useMemo(
    () => CELEBRATIONS.map((item) => ({
      ...item,
      data: dashboard?.celebraciones?.[item.key],
    })),
    [dashboard],
  );

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand__mark">PC</div>
          <div><strong>Planifica</strong><span>Compras de temporada</span></div>
        </div>
        <div className="sidebar__section-label">MENÚ PRINCIPAL</div>
        <nav className="sidebar__nav" aria-label="Navegación principal">
          <button className="nav-item nav-item--active" type="button"><span>▦</span> Dashboard</button>
          <button className="nav-item" type="button" disabled><span>▤</span> Productos <small>Próximo</small></button>
          <button className="nav-item" type="button" disabled><span>◫</span> Presupuestos <small>Próximo</small></button>
          <button className="nav-item" type="button" disabled><span>▧</span> Años <small>Próximo</small></button>
        </nav>
        <div className="sidebar__footer">
          <span className="status-dot" /> API de planificación
          <small>Versión inicial · MVP</small>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div><span className="eyebrow">GESTIÓN DE TEMPORADA</span><h1>Dashboard</h1></div>
          <label className="year-select">
            <span>Año de planificación</span>
            <select value={selectedYear} onChange={(event) => setSelectedYear(event.target.value)} disabled={!years.length}>
              {years.length ? years.map((item) => <option key={item.id} value={item.anio}>{formatYear(item.anio)}</option>) : <option value="">Sin años</option>}
            </select>
          </label>
        </header>

        <section className="page-intro">
          <div><h2>Resumen de compras</h2><p>Controla tu presupuesto y el avance de las celebraciones.</p></div>
          {selectedYear && <span className="year-pill">Planificación {selectedYear}</span>}
        </section>

        {(loadingYears || loadingDashboard) && <div className="notice notice--loading">Cargando información del sistema…</div>}
        {error && <div className="notice notice--error" role="alert">{error}</div>}

        {!loadingYears && !years.length && !error && (
          <div className="empty-state"><div className="empty-state__icon">＋</div><h2>Aún no hay años de planificación</h2><p>Cuando registres el primer año, sus indicadores aparecerán aquí.</p></div>
        )}

        {dashboard && (
          <>
            <section className="metrics-grid" aria-label="Indicadores generales">
              <MetricCard label="Presupuesto general" value={formatCurrency(dashboard.presupuesto_general)} hint="Presupuesto configurado" />
              <MetricCard label="Gasto real" value={formatCurrency(dashboard.gasto_real_general)} hint="Compras realizadas" accent="green" />
              <MetricCard label="Saldo disponible" value={formatCurrency(dashboard.saldo_general)} hint="Presupuesto menos gasto real" accent="gold" />
              <MetricCard label="Gasto estimado" value={formatCurrency(dashboard.gasto_estimado_general)} hint="Productos pendientes" accent="slate" />
            </section>

            <section className="section-block">
              <div className="section-heading"><div><h2>Celebraciones</h2><p>Indicadores por temporada</p></div></div>
              <div className="celebrations-grid">
                {celebrationCards.map((item) => <CelebrationCard key={item.key} celebration={item.data} label={item.label} icon={item.icon} />)}
              </div>
            </section>

            <section className="section-block">
              <div className="section-heading"><div><h2>Alertas y seguimiento</h2><p>Notificaciones generadas por las reglas del sistema</p></div></div>
              {dashboard.alertas?.length ? (
                <div className="alerts-list">{dashboard.alertas.map((alert, index) => (
                  <article className="alert-item" key={`${alert.codigo}-${index}`}>
                    <span className="alert-item__icon">!</span>
                    <div><strong>{alert.mensaje}</strong><span>{alert.alcance}</span></div>
                  </article>
                ))}</div>
              ) : <div className="quiet-state">No hay alertas para este año.</div>}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
