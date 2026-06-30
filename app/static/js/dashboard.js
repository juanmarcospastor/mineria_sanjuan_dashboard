async function loadCharts() {
  const params = new URLSearchParams(window.dashboardParams);
  const response = await fetch(`/api/charts?${params.toString()}`);
  const data = await response.json();

  const config = {responsive: true, displaylogo: false};
  const chartMap = {
    "chart-exportaciones": data.exportaciones,
    "chart-provincias": data.provincias,
    "chart-productos": data.productos,
    "chart-destinos": data.destinos,
    "chart-precio-oro": data.precio_oro,
    "chart-precio-plata": data.precio_plata,
    "chart-precio-cobre": data.precio_cobre,
    "chart-precio-litio": data.precio_litio,
    "chart-volumen": data.volumen,
    "chart-balance": data.balance
  };

  Object.entries(chartMap).forEach(([id, figJson]) => {
    const fig = JSON.parse(figJson);
    Plotly.newPlot(id, fig.data, fig.layout, config);
  });
}

document.addEventListener("DOMContentLoaded", loadCharts);

