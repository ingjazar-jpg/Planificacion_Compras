const API_PREFIX = "/api/v1";

export class ApiError extends Error {
  constructor(message, { status = 0, code = "ERROR_API", details = [] } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = Array.isArray(details) ? details : [];
  }
}

async function request(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_PREFIX}${path}`, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new ApiError("No fue posible conectar con el servidor. Verifica que FastAPI esté ejecutándose.");
  }

  if (response.status === 204) return null;

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const error = payload?.error;
    const validationMessage = Array.isArray(payload?.detail)
      ? payload.detail.map((item) => item.msg).filter(Boolean).join(" ")
      : null;

    throw new ApiError(
      error?.mensaje || validationMessage || "Ocurrió un error al procesar la solicitud.",
      {
        status: response.status,
        code: error?.codigo || "ERROR_API",
        details: error?.detalles || payload?.detail || [],
      },
    );
  }

  return payload;
}

function jsonBody(data) {
  return JSON.stringify(data);
}

export const api = {
  listYears: () => request("/anios"),
  getYear: (year) => request(`/anios/${year}`),
  createYear: (data) => request("/anios", { method: "POST", body: jsonBody(data) }),
  updateGeneralBudget: (year, value) =>
    request(`/anios/${year}/presupuesto-general`, {
      method: "PUT",
      body: jsonBody({ presupuesto_general: value }),
    }),
  updateCelebrationBudget: (year, type, value) =>
    request(`/anios/${year}/celebraciones/${type}/presupuesto`, {
      method: "PUT",
      body: jsonBody({ presupuesto: value }),
    }),
  listProducts: (year, type, filters = {}) => {
    const params = new URLSearchParams();
    if (filters.categoria) params.set("categoria", filters.categoria);
    if (filters.estado) params.set("estado", filters.estado);
    if (filters.buscar?.trim()) params.set("buscar", filters.buscar.trim());
    const query = params.toString();
    return request(`/anios/${year}/celebraciones/${type}/productos${query ? `?${query}` : ""}`);
  },
  createProduct: (year, type, data) =>
    request(`/anios/${year}/celebraciones/${type}/productos`, {
      method: "POST",
      body: jsonBody(data),
    }),
  getProduct: (id) => request(`/productos/${id}`),
  updatePendingProduct: (id, data) =>
    request(`/productos/${id}`, { method: "PUT", body: jsonBody(data) }),
  deletePendingProduct: (id) => request(`/productos/${id}`, { method: "DELETE" }),
  markPurchased: (id, realPrice) =>
    request(`/productos/${id}/comprar`, {
      method: "PATCH",
      body: jsonBody({ precio_unitario_real: realPrice }),
    }),
  correctPurchasedProduct: (id, data) =>
    request(`/productos/${id}/correccion-compra`, {
      method: "PATCH",
      body: jsonBody(data),
    }),
  getDashboard: (year) => request(`/anios/${year}/dashboard`),
  getAnnualSummary: (year) => request(`/anios/${year}/resumen`),
  getCelebrationSummary: (year, type) =>
    request(`/anios/${year}/celebraciones/${type}/resumen`),
  getCategoryStatistics: (year) =>
    request(`/anios/${year}/estadisticas/categorias`),
  getCatalogs: () => request("/catalogos"),
};
