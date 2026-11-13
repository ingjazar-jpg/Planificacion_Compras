import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./services/api.js";
import { formatCurrency, formatPercent, formatYear } from "./utils/formatters.js";
import "./App.css";

const CELEBRATIONS = [
  { key: "navidad", label: "Navidad" },
  { key: "fin_anio", label: "Fin de Año" },
];

const EMPTY_PRODUCT = {
  nombre: "",
  descripcion: "",
  categoria: "alimentos",
  cantidad: "1",
  unidad: "unidad",
  precio_unitario_estimado: "0",
  precio_unitario_real: "0",
};

function moneyInput(value) {
  if (value === null || value === undefined) return "";
  return String(value);
}

function MetricCard({ label, value, hint, accent = "blue" }) {
  return <article className={`metric-card metric-card--${accent}`}>
    <span className="metric-card__label">{label}</span>
    <strong className="metric-card__value">{value}</strong>
    {hint && <span className="metric-card__hint">{hint}</span>}
  </article>;
}

function CelebrationCard({ celebration, label }) {
  if (!celebration) return null;
  const progress = Math.min(100, Math.max(0, Number(celebration.avance_compras) || 0));
  return <article className="celebration-card">
    <div className="celebration-card__heading">
      <span className="celebration-card__icon" aria-hidden="true">{label === "Navidad" ? "✦" : "◈"}</span>
      <div><h3>{label}</h3><p>Resumen de la celebración</p></div>
    </div>
    <div className="celebration-card__grid">
      <div><span>Presupuesto</span><strong>{formatCurrency(celebration.presupuesto)}</strong></div>
      <div><span>Gasto real</span><strong>{formatCurrency(celebration.gasto_real)}</strong></div>
      <div><span>Saldo</span><strong>{formatCurrency(celebration.saldo)}</strong></div>
    </div>
    <div className="progress-heading"><span>Avance de compras</span><strong>{formatPercent(celebration.avance_compras)}</strong></div>
    <div className="progress-track" role="progressbar" aria-valuenow={progress} aria-valuemin="0" aria-valuemax="100"><span style={{ width: `${progress}%` }} /></div>
    <div className="celebration-card__counts"><span>{celebration.productos_comprados ?? 0} comprados</span><span>{celebration.productos_pendientes ?? 0} pendientes</span></div>
  </article>;
}

function Field({ label, children, hint }) {
  return <label className="form-field"><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>;
}

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [years, setYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [yearDetail, setYearDetail] = useState(null);
  const [catalogs, setCatalogs] = useState({ categorias: [], unidades: [], estados: [] });
  const [products, setProducts] = useState([]);
  const [celebration, setCelebration] = useState("navidad");
  const [filters, setFilters] = useState({ categoria: "", estado: "", buscar: "" });
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [yearForm, setYearForm] = useState({ anio: String(new Date().getFullYear()), presupuesto_general: "", presupuesto_navidad: "", presupuesto_fin_anio: "" });
  const [budgetForm, setBudgetForm] = useState({ presupuesto_general: "", navidad: "", fin_anio: "" });
  const [productModal, setProductModal] = useState(null);
  const [productForm, setProductForm] = useState(EMPTY_PRODUCT);
  const [purchaseProduct, setPurchaseProduct] = useState(null);
  const [purchasePrice, setPurchasePrice] = useState("");

  const isReadOnly = selectedYear && Number(selectedYear) < new Date().getFullYear();

  const refreshYears = useCallback(async (preferredYear) => {
    const data = await api.listYears();
    const available = data?.anios ?? [];
    setYears(available);
    if (preferredYear && available.some((item) => String(item.anio) === String(preferredYear))) {
      setSelectedYear(String(preferredYear));
    } else if (!available.some((item) => String(item.anio) === String(selectedYear))) {
      setSelectedYear(available.length ? String(available[0].anio) : "");
    }
    return available;
  }, [selectedYear]);

  const refreshYearData = useCallback(async (year = selectedYear) => {
    if (!year) {
      setDashboard(null);
      setYearDetail(null);
      return;
    }
    const [dashboardData, detailData] = await Promise.all([
      api.getDashboard(year),
      api.getYear(year),
    ]);
    setDashboard(dashboardData);
    setYearDetail(detailData);
    setBudgetForm({
      presupuesto_general: moneyInput(detailData.presupuesto_general),
      navidad: moneyInput(detailData.celebraciones?.find((item) => item.tipo === "Navidad")?.presupuesto),
      fin_anio: moneyInput(detailData.celebraciones?.find((item) => item.tipo === "Fin de Año")?.presupuesto),
    });
  }, [selectedYear]);

  const refreshProducts = useCallback(async () => {
    if (!selectedYear) {
      setProducts([]);
      return;
    }
    const data = await api.listProducts(selectedYear, celebration, filters);
    setProducts(data?.productos ?? []);
  }, [selectedYear, celebration, filters]);

  useEffect(() => {
    let active = true;
    Promise.all([api.listYears(), api.getCatalogs()])
      .then(([yearData, catalogData]) => {
        if (!active) return;
        const available = yearData?.anios ?? [];
        setYears(available);
        setSelectedYear(available.length ? String(available[0].anio) : "");
        setCatalogs(catalogData);
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!selectedYear) return;
    let active = true;
    setBusy(true);
    Promise.all([api.getDashboard(selectedYear), api.getYear(selectedYear)])
      .then(([dashboardData, detailData]) => {
        if (!active) return;
        setDashboard(dashboardData);
        setYearDetail(detailData);
        setBudgetForm({
          presupuesto_general: moneyInput(detailData.presupuesto_general),
          navidad: moneyInput(detailData.celebraciones?.find((item) => item.tipo === "Navidad")?.presupuesto),
          fin_anio: moneyInput(detailData.celebraciones?.find((item) => item.tipo === "Fin de Año")?.presupuesto),
        });
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setBusy(false));
    return () => { active = false; };
  }, [selectedYear]);

  useEffect(() => {
    if (page !== "products" || !selectedYear) return;
    let active = true;
    api.listProducts(selectedYear, celebration, filters)
      .then((data) => active && setProducts(data?.productos ?? []))
      .catch((err) => active && setError(err.message));
    return () => { active = false; };
  }, [page, selectedYear, celebration, filters]);

  const celebrationCards = useMemo(() => CELEBRATIONS.map((item) => ({
    ...item,
    data: dashboard?.celebraciones?.[item.key],
  })), [dashboard]);

  async function handleCreateYear(event) {
    event.preventDefault();
    setBusy(true); setError(""); setNotice("");
    try {
      const payload = {
        anio: Number(yearForm.anio),
        presupuesto_general: yearForm.presupuesto_general || null,
        presupuesto_navidad: yearForm.presupuesto_navidad || null,
        presupuesto_fin_anio: yearForm.presupuesto_fin_anio || null,
      };
      await api.createYear(payload);
      await refreshYears(yearForm.anio);
      setYearForm({ anio: String(Number(yearForm.anio) + 1), presupuesto_general: "", presupuesto_navidad: "", presupuesto_fin_anio: "" });
      setNotice("Año de planificación creado correctamente.");
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  async function handleSaveBudgets(event) {
    event.preventDefault();
    if (isReadOnly) return;
    setBusy(true); setError(""); setNotice("");
    try {
      await api.updateGeneralBudget(selectedYear, budgetForm.presupuesto_general || null);
      await api.updateCelebrationBudget(selectedYear, "navidad", budgetForm.navidad || null);
      await api.updateCelebrationBudget(selectedYear, "fin_anio", budgetForm.fin_anio || null);
      await refreshYearData(selectedYear);
      await api.getDashboard(selectedYear).then(setDashboard);
      setNotice("Presupuestos actualizados correctamente.");
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  function openNewProduct() {
    setProductForm(EMPTY_PRODUCT);
    setProductModal({ mode: "create", product: null });
  }

  function openEditProduct(product, correction = false) {
    setProductForm({
      nombre: product.nombre,
      descripcion: product.descripcion ?? "",
      categoria: catalogs.categorias.find((item) => item.etiqueta === product.categoria)?.valor ?? "otros",
      cantidad: product.cantidad,
      unidad: catalogs.unidades.find((item) => item.etiqueta === product.unidad)?.valor ?? "unidad",
      precio_unitario_estimado: product.precio_unitario_estimado,
      precio_unitario_real: product.precio_unitario_real ?? "0",
    });
    setProductModal({ mode: correction ? "correction" : "edit", product });
  }

  async function handleSaveProduct(event) {
    event.preventDefault();
    setBusy(true); setError(""); setNotice("");
    const payload = {
      nombre: productForm.nombre.trim(),
      descripcion: productForm.descripcion.trim() || null,
      categoria: productForm.categoria,
      cantidad: productForm.cantidad,
      unidad: productForm.unidad,
      precio_unitario_estimado: productForm.precio_unitario_estimado,
    };
    try {
      if (productModal.mode === "create") {
        await api.createProduct(selectedYear, celebration, payload);
        setNotice("Producto registrado correctamente.");
      } else if (productModal.mode === "edit") {
        await api.updatePendingProduct(productModal.product.id, payload);
        setNotice("Producto actualizado correctamente.");
      } else {
        await api.correctPurchasedProduct(productModal.product.id, {
          ...payload,
          precio_unitario_real: productForm.precio_unitario_real,
        });
        setNotice("Corrección de compra guardada correctamente.");
      }
      setProductModal(null);
      await refreshProducts();
      await refreshYearData(selectedYear);
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  async function handleDeleteProduct(product) {
    if (!window.confirm(`¿Eliminar el producto "${product.nombre}"? Esta acción no se puede deshacer.`)) return;
    setBusy(true); setError(""); setNotice("");
    try {
      await api.deletePendingProduct(product.id);
      setNotice("Producto eliminado.");
      await refreshProducts();
      await refreshYearData(selectedYear);
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  function openPurchase(product) {
    setPurchaseProduct(product);
    setPurchasePrice(product.precio_unitario_estimado ?? "");
  }

  async function handlePurchase(event) {
    event.preventDefault();
    if (!purchaseProduct) return;
    setBusy(true); setError(""); setNotice("");
    try {
      await api.markPurchased(purchaseProduct.id, purchasePrice);
      setPurchaseProduct(null);
      setNotice("Producto marcado como comprado.");
      await refreshProducts();
      await refreshYearData(selectedYear);
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  const pageTitle = { dashboard: "Dashboard", years: "Años", budgets: "Presupuestos", products: "Productos" }[page];

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand__mark">PC</div><div><strong>Planifica</strong><span>Compras de temporada</span></div></div>
      <div className="sidebar__section-label">MENÚ PRINCIPAL</div>
      <nav className="sidebar__nav" aria-label="Navegación principal">
        <button className={`nav-item ${page === "dashboard" ? "nav-item--active" : ""}`} onClick={() => setPage("dashboard")}><span>▦</span> Dashboard</button>
        <button className={`nav-item ${page === "products" ? "nav-item--active" : ""}`} onClick={() => setPage("products")}><span>▤</span> Productos</button>
        <button className={`nav-item ${page === "budgets" ? "nav-item--active" : ""}`} onClick={() => setPage("budgets")}><span>◫</span> Presupuestos</button>
        <button className={`nav-item ${page === "years" ? "nav-item--active" : ""}`} onClick={() => setPage("years")}><span>▧</span> Años</button>
      </nav>
      <div className="sidebar__footer"><span className="status-dot" /> API de planificación<small>Frontend MVP · v1.0</small></div>
    </aside>

    <main className="main-content">
      <header className="topbar">
        <div><span className="eyebrow">GESTIÓN DE TEMPORADA</span><h1>{pageTitle}</h1></div>
        <label className="year-select"><span>Año de planificación</span>
          <select value={selectedYear} onChange={(event) => setSelectedYear(event.target.value)} disabled={!years.length}>
            {years.length ? years.map((item) => <option key={item.id} value={item.anio}>{formatYear(item.anio)}</option>) : <option value="">Sin años</option>}
          </select>
        </label>
      </header>

      {error && <div className="notice notice--error" role="alert">{error}<button type="button" className="notice-close" onClick={() => setError("")}>Cerrar</button></div>}
      {notice && <div className="notice notice--success" role="status">{notice}<button type="button" className="notice-close" onClick={() => setNotice("")}>Cerrar</button></div>}
      {(loading || busy) && <div className="notice notice--loading">{loading ? "Cargando información del sistema…" : "Procesando operación…"}</div>}

      {!loading && !years.length && page !== "years" && <div className="empty-state"><div className="empty-state__icon">＋</div><h2>Aún no hay años de planificación</h2><p>Registra el primer año para comenzar a organizar tus compras.</p><button className="primary-button" onClick={() => setPage("years")}>Crear año</button></div>}

      {page === "dashboard" && dashboard && <>
        <section className="page-intro"><div><h2>Resumen de compras</h2><p>Controla tu presupuesto y el avance de las celebraciones.</p></div><span className="year-pill">Planificación {selectedYear}</span></section>
        <section className="metrics-grid" aria-label="Indicadores generales">
          <MetricCard label="Presupuesto general" value={formatCurrency(dashboard.presupuesto_general)} hint="Presupuesto configurado" />
          <MetricCard label="Gasto real" value={formatCurrency(dashboard.gasto_real_general)} hint="Compras realizadas" accent="green" />
          <MetricCard label="Saldo disponible" value={formatCurrency(dashboard.saldo_general)} hint="Presupuesto menos gasto real" accent="gold" />
          <MetricCard label="Gasto estimado" value={formatCurrency(dashboard.gasto_estimado_general)} hint="Productos pendientes" accent="slate" />
        </section>
        <section className="section-block"><div className="section-heading"><div><h2>Celebraciones</h2><p>Indicadores por temporada</p></div></div>
          <div className="celebrations-grid">{celebrationCards.map((item) => <CelebrationCard key={item.key} celebration={item.data} label={item.label} />)}</div>
        </section>
        <section className="section-block"><div className="section-heading"><div><h2>Alertas y seguimiento</h2><p>Notificaciones generadas por las reglas del sistema</p></div></div>
          {dashboard.alertas?.length ? <div className="alerts-list">{dashboard.alertas.map((alert, index) => <article className="alert-item" key={`${alert.codigo}-${index}`}><span className="alert-item__icon">!</span><div><strong>{alert.mensaje}</strong><span>{alert.alcance}</span></div></article>)}</div> : <div className="quiet-state">No hay alertas para este año.</div>}
        </section>
      </>}

      {page === "years" && <section className="page-section">
        <div className="section-heading"><div><h2>Crear año de planificación</h2><p>Define el periodo y los presupuestos iniciales opcionales.</p></div></div>
        <form className="panel form-grid" onSubmit={handleCreateYear}>
          <Field label="Año"><input type="number" min={new Date().getFullYear()} required value={yearForm.anio} onChange={(e) => setYearForm({ ...yearForm, anio: e.target.value })} /></Field>
          <Field label="Presupuesto general (COP)"><input type="number" min="0" step="0.01" value={yearForm.presupuesto_general} onChange={(e) => setYearForm({ ...yearForm, presupuesto_general: e.target.value })} placeholder="Opcional" /></Field>
          <Field label="Presupuesto Navidad (COP)"><input type="number" min="0" step="0.01" value={yearForm.presupuesto_navidad} onChange={(e) => setYearForm({ ...yearForm, presupuesto_navidad: e.target.value })} placeholder="Opcional" /></Field>
          <Field label="Presupuesto Fin de Año (COP)"><input type="number" min="0" step="0.01" value={yearForm.presupuesto_fin_anio} onChange={(e) => setYearForm({ ...yearForm, presupuesto_fin_anio: e.target.value })} placeholder="Opcional" /></Field>
          <div className="form-actions"><button className="primary-button" disabled={busy}>Crear año</button></div>
        </form>
        <div className="section-heading section-heading--spaced"><div><h2>Años registrados</h2><p>Selecciona un año para consultar su planificación.</p></div></div>
        <div className="year-list">{years.map((item) => <button className={`year-list-item ${String(item.anio) === selectedYear ? "is-selected" : ""}`} key={item.id} onClick={() => { setSelectedYear(String(item.anio)); setPage("dashboard"); }}><strong>{item.anio}</strong><span>{formatCurrency(item.presupuesto_general)}</span><span>{Number(item.anio) < new Date().getFullYear() ? "Solo lectura" : "Editable"}</span></button>)}</div>
      </section>}

      {page === "budgets" && yearDetail && <section className="page-section">
        <div className="section-heading"><div><h2>Presupuestos de {selectedYear}</h2><p>Los valores vacíos o cero se interpretan como presupuesto no configurado.</p></div>{isReadOnly && <span className="readonly-tag">Año histórico · Solo lectura</span>}</div>
        <form className="panel form-grid" onSubmit={handleSaveBudgets}>
          <Field label="Presupuesto general (COP)"><input type="number" min="0" step="0.01" disabled={isReadOnly} value={budgetForm.presupuesto_general} onChange={(e) => setBudgetForm({ ...budgetForm, presupuesto_general: e.target.value })} placeholder="Sin configurar" /></Field>
          <Field label="Presupuesto Navidad (COP)"><input type="number" min="0" step="0.01" disabled={isReadOnly} value={budgetForm.navidad} onChange={(e) => setBudgetForm({ ...budgetForm, navidad: e.target.value })} placeholder="Sin configurar" /></Field>
          <Field label="Presupuesto Fin de Año (COP)"><input type="number" min="0" step="0.01" disabled={isReadOnly} value={budgetForm.fin_anio} onChange={(e) => setBudgetForm({ ...budgetForm, fin_anio: e.target.value })} placeholder="Sin configurar" /></Field>
          {!isReadOnly && <div className="form-actions"><button className="primary-button" disabled={busy}>Guardar presupuestos</button></div>}
        </form>
        <div className="budget-summary-grid">{CELEBRATIONS.map((item) => {
          const record = yearDetail.celebraciones?.find((row) => row.tipo === item.label);
          return <article className="panel budget-summary" key={item.key}><span>{item.label}</span><strong>{formatCurrency(record?.presupuesto)}</strong><small>Presupuesto configurado</small></article>;
        })}</div>
      </section>}

      {page === "products" && <section className="page-section">
        <div className="section-heading section-heading--wrap"><div><h2>Productos de temporada</h2><p>Registra, consulta y actualiza los productos de cada celebración.</p></div><button className="primary-button" disabled={!!isReadOnly || !selectedYear} onClick={openNewProduct}>＋ Agregar producto</button></div>
        {isReadOnly && <div className="readonly-banner">Este año es histórico. Los productos se pueden consultar, pero no modificar.</div>}
        <div className="toolbar panel">
          <Field label="Celebración"><select value={celebration} onChange={(e) => setCelebration(e.target.value)}>{CELEBRATIONS.map((item) => <option key={item.key} value={item.key}>{item.label}</option>)}</select></Field>
          <Field label="Categoría"><select value={filters.categoria} onChange={(e) => setFilters({ ...filters, categoria: e.target.value })}><option value="">Todas</option>{catalogs.categorias.map((item) => <option key={item.valor} value={item.valor}>{item.etiqueta}</option>)}</select></Field>
          <Field label="Estado"><select value={filters.estado} onChange={(e) => setFilters({ ...filters, estado: e.target.value })}><option value="">Todos</option>{catalogs.estados.map((item) => <option key={item.valor} value={item.valor}>{item.etiqueta}</option>)}</select></Field>
          <Field label="Buscar"><input value={filters.buscar} onChange={(e) => setFilters({ ...filters, buscar: e.target.value })} placeholder="Nombre o descripción" /></Field>
        </div>
        <div className="panel table-panel">
          {products.length ? <div className="table-scroll"><table className="products-table"><thead><tr><th>Producto</th><th>Categoría</th><th>Cantidad</th><th>Precio estimado</th><th>Precio real</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>
            {products.map((product) => <tr key={product.id}><td><strong>{product.nombre}</strong>{product.descripcion && <small>{product.descripcion}</small>}</td><td>{product.categoria}</td><td>{product.cantidad} {product.unidad}</td><td>{formatCurrency(product.precio_unitario_estimado)}</td><td>{formatCurrency(product.precio_unitario_real)}</td><td><span className={`state-pill state-pill--${product.estado}`}>{product.estado === "comprado" ? "Comprado" : "Pendiente"}</span></td><td><div className="row-actions">
              {product.estado === "pendiente" ? <><button type="button" onClick={() => openEditProduct(product)} disabled={!!isReadOnly}>Editar</button><button type="button" onClick={() => openPurchase(product)} disabled={!!isReadOnly}>Comprar</button><button type="button" className="danger-link" onClick={() => handleDeleteProduct(product)} disabled={!!isReadOnly}>Eliminar</button></> : <button type="button" onClick={() => openEditProduct(product, true)} disabled={!!isReadOnly}>Corregir compra</button>}
            </div></td></tr>)}
          </tbody></table></div> : <div className="quiet-state">No hay productos que coincidan con los filtros.</div>}
        </div>
      </section>}
    </main>

    {productModal && <div className="modal-backdrop" role="presentation" onMouseDown={(e) => e.target === e.currentTarget && setProductModal(null)}><section className="modal-card" role="dialog" aria-modal="true" aria-labelledby="product-modal-title">
      <div className="modal-heading"><div><h2 id="product-modal-title">{productModal.mode === "create" ? "Agregar producto" : productModal.mode === "edit" ? "Editar producto pendiente" : "Corregir compra"}</h2><p>{productModal.mode === "correction" ? "El estado comprado y la identidad del producto se conservan." : "Completa los datos del producto."}</p></div><button className="icon-button" type="button" onClick={() => setProductModal(null)}>×</button></div>
      <form className="form-grid" onSubmit={handleSaveProduct}>
        <Field label="Nombre"><input required minLength="1" value={productForm.nombre} onChange={(e) => setProductForm({ ...productForm, nombre: e.target.value })} /></Field>
        <Field label="Descripción"><input value={productForm.descripcion} onChange={(e) => setProductForm({ ...productForm, descripcion: e.target.value })} /></Field>
        <Field label="Categoría"><select value={productForm.categoria} onChange={(e) => setProductForm({ ...productForm, categoria: e.target.value })}>{catalogs.categorias.map((item) => <option key={item.valor} value={item.valor}>{item.etiqueta}</option>)}</select></Field>
        <Field label="Cantidad"><input type="number" min="0.01" step="0.01" required value={productForm.cantidad} onChange={(e) => setProductForm({ ...productForm, cantidad: e.target.value })} /></Field>
        <Field label="Unidad"><select value={productForm.unidad} onChange={(e) => setProductForm({ ...productForm, unidad: e.target.value })}>{catalogs.unidades.map((item) => <option key={item.valor} value={item.valor}>{item.etiqueta}</option>)}</select></Field>
        <Field label="Precio unitario estimado (COP)"><input type="number" min="0" step="0.01" required value={productForm.precio_unitario_estimado} onChange={(e) => setProductForm({ ...productForm, precio_unitario_estimado: e.target.value })} /></Field>
        {productModal.mode === "correction" && <Field label="Precio unitario real (COP)"><input type="number" min="0" step="0.01" required value={productForm.precio_unitario_real} onChange={(e) => setProductForm({ ...productForm, precio_unitario_real: e.target.value })} /></Field>}
        <div className="form-actions"><button type="button" className="secondary-button" onClick={() => setProductModal(null)}>Cancelar</button><button className="primary-button" disabled={busy}>Guardar</button></div>
      </form>
    </section></div>}

    {purchaseProduct && <div className="modal-backdrop"><section className="modal-card modal-card--narrow" role="dialog" aria-modal="true" aria-labelledby="purchase-modal-title">
      <div className="modal-heading"><div><h2 id="purchase-modal-title">Registrar compra</h2><p>{purchaseProduct.nombre}</p></div><button className="icon-button" type="button" onClick={() => setPurchaseProduct(null)}>×</button></div>
      <form onSubmit={handlePurchase}><Field label="Precio unitario real (COP)"><input type="number" min="0" step="0.01" required value={purchasePrice} onChange={(e) => setPurchasePrice(e.target.value)} /></Field><p className="field-note">El precio real es obligatorio. Se permite registrar cero.</p><div className="form-actions"><button type="button" className="secondary-button" onClick={() => setPurchaseProduct(null)}>Cancelar</button><button className="primary-button" disabled={busy}>Confirmar compra</button></div></form>
    </section></div>}
  </div>;
}
