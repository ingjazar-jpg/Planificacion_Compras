const currencyFormatter = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function formatCurrency(value) {
  if (value === null || value === undefined || value === "") return "Sin configurar";
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return "—";
  return currencyFormatter.format(numericValue);
}

export function formatPercent(value) {
  if (value === null || value === undefined || value === "") return "0 %";
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? `${numericValue.toLocaleString("es-CO", { maximumFractionDigits: 1 })} %` : "—";
}

export function formatYear(value) {
  return Number.isInteger(Number(value)) ? String(value) : "—";
}
