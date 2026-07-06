from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "modelo_estrella_ventas.xlsx"
OUTPUT_DIR = BASE_DIR / "graficos"
OUTPUT_PATH = OUTPUT_DIR / "informe_modelo_estrella.html"


def money(value):
    return f"${value:,.2f}"


def number(value):
    return f"{value:,.0f}"


def pct(value):
    return f"{value:.2%}"


def load_model():
    sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)

    fact = sheets["Fact_Ventas"].copy()
    cliente = sheets["Dim_Cliente"].copy()
    producto = sheets["Dim_Producto"].copy()
    vendedor = sheets["Dim_Vendedor"].copy()
    tiempo = sheets["Dim_Tiempo"].copy()

    tiempo["Fecha"] = pd.to_datetime(tiempo["Fecha"])
    for col in ["Cantidad", "Monto_Bruto", "Descuento", "Monto_Neto"]:
        fact[col] = pd.to_numeric(fact[col], errors="coerce")

    df = (
        fact.merge(cliente, on="ID_Cliente", how="left")
        .merge(producto, on="ID_Producto", how="left")
        .merge(tiempo, on="ID_Tiempo", how="left")
        .merge(vendedor, on="ID_Vendedor", how="left")
    )

    return df, fact, cliente, producto, vendedor, tiempo


def style_figure(fig, height=360):
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=54, b=34),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Segoe UI, Arial, sans-serif", color="#23313d"),
        title=dict(font=dict(size=17), x=0.01, xanchor="left"),
        hoverlabel=dict(bgcolor="#23313d", font_size=12, font_color="white"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#edf1f5", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#edf1f5", zeroline=False)
    return fig


def chart_html(fig, include_js=False):
    return pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn" if include_js else False,
        config={"displaylogo": False, "responsive": True},
    )


def build_report():
    df, fact, cliente, producto, vendedor, tiempo = load_model()
    OUTPUT_DIR.mkdir(exist_ok=True)

    total_ventas = df["Monto_Neto"].sum()
    total_bruto = df["Monto_Bruto"].sum()
    total_descuentos = df["Descuento"].sum()
    total_cantidad = df["Cantidad"].sum()
    transacciones = df["ID_Venta"].nunique()
    clientes = df["ID_Cliente"].nunique()
    productos = df["ID_Producto"].nunique()
    ticket_promedio = total_ventas / transacciones
    descuento_pct = total_descuentos / total_bruto if total_bruto else 0

    ventas_categoria = (
        df.groupby("Categoría", as_index=False)["Monto_Neto"]
        .sum()
        .sort_values("Monto_Neto", ascending=False)
    )
    ventas_categoria["Monto_fmt"] = ventas_categoria["Monto_Neto"].map(money)

    top_paises = (
        df.groupby("País", as_index=False)["Monto_Neto"]
        .sum()
        .sort_values("Monto_Neto", ascending=False)
        .head(10)
    )

    ventas_mes = (
        df.assign(Periodo=df["Fecha"].dt.to_period("M").dt.to_timestamp())
        .groupby("Periodo", as_index=False)["Monto_Neto"]
        .sum()
    )

    ventas_region = (
        df.groupby("Región", as_index=False)["Monto_Neto"]
        .sum()
        .sort_values("Monto_Neto", ascending=False)
    )

    top_productos = (
        df.groupby("Nombre_Producto", as_index=False)
        .agg(Monto_Neto=("Monto_Neto", "sum"), Cantidad=("Cantidad", "sum"))
        .sort_values("Monto_Neto", ascending=False)
        .head(10)
    )

    descuentos = (
        df.groupby("Nombre_Producto", as_index=False)
        .agg(Descuento=("Descuento", "sum"), Monto_Neto=("Monto_Neto", "sum"), Cantidad=("Cantidad", "sum"))
        .sort_values("Monto_Neto", ascending=False)
    )

    ventas_segmento = (
        df.groupby("Segmento", as_index=False)["Monto_Neto"]
        .sum()
        .sort_values("Monto_Neto", ascending=False)
    )

    ventas_trimestre = (
        df.groupby("Trimestre", as_index=False)["Monto_Neto"]
        .sum()
        .sort_values("Trimestre")
    )

    fig_categoria = px.bar(
        ventas_categoria,
        x="Categoría",
        y="Monto_Neto",
        text="Monto_fmt",
        title="Ventas por categoría de producto",
        color="Categoría",
        color_discrete_sequence=["#0f766e", "#2563eb", "#c2410c", "#7c3aed", "#be123c"],
    )
    fig_categoria.update_traces(textposition="outside", hovertemplate="%{x}<br>Ventas: %{y:$,.2f}<extra></extra>")
    style_figure(fig_categoria, 390)

    fig_paises = px.bar(
        top_paises.sort_values("Monto_Neto"),
        x="Monto_Neto",
        y="País",
        orientation="h",
        title="Top 10 países por ventas",
        color="Monto_Neto",
        color_continuous_scale=["#dbeafe", "#1d4ed8"],
    )
    fig_paises.update_traces(hovertemplate="%{y}<br>Ventas: %{x:$,.2f}<extra></extra>")
    fig_paises.update_layout(coloraxis_showscale=False)
    style_figure(fig_paises, 410)

    fig_tiempo = px.line(
        ventas_mes,
        x="Periodo",
        y="Monto_Neto",
        markers=True,
        title="Evolución mensual de ventas",
    )
    fig_tiempo.update_traces(line=dict(color="#0f766e", width=3), marker=dict(size=8), hovertemplate="%{x|%b %Y}<br>Ventas: %{y:$,.2f}<extra></extra>")
    style_figure(fig_tiempo, 360)

    fig_region = px.pie(
        ventas_region,
        names="Región",
        values="Monto_Neto",
        title="Participación de ventas por región",
        hole=0.48,
        color_discrete_sequence=["#0f766e", "#2563eb", "#c2410c", "#7c3aed", "#be123c"],
    )
    fig_region.update_traces(textposition="inside", textinfo="percent+label", hovertemplate="%{label}<br>Ventas: %{value:$,.2f}<extra></extra>")
    style_figure(fig_region, 360)

    fig_productos = px.bar(
        top_productos.sort_values("Monto_Neto"),
        x="Monto_Neto",
        y="Nombre_Producto",
        orientation="h",
        title="Top 10 productos por ventas",
        color="Cantidad",
        color_continuous_scale=["#fef3c7", "#c2410c"],
    )
    fig_productos.update_traces(hovertemplate="%{y}<br>Ventas: %{x:$,.2f}<extra></extra>")
    fig_productos.update_layout(coloraxis_colorbar=dict(title="Unidades"))
    style_figure(fig_productos, 430)

    fig_descuentos = px.scatter(
        descuentos,
        x="Descuento",
        y="Monto_Neto",
        size="Cantidad",
        color="Monto_Neto",
        hover_name="Nombre_Producto",
        title="Relación entre descuentos y ventas netas",
        color_continuous_scale=["#ede9fe", "#7c3aed"],
    )
    fig_descuentos.update_traces(hovertemplate="<b>%{hovertext}</b><br>Descuento: %{x:$,.2f}<br>Ventas: %{y:$,.2f}<extra></extra>")
    fig_descuentos.update_layout(coloraxis_showscale=False)
    style_figure(fig_descuentos, 390)

    fig_segmento = px.bar(
        ventas_segmento,
        x="Segmento",
        y="Monto_Neto",
        title="Ventas por segmento de cliente",
        color="Segmento",
        color_discrete_sequence=["#2563eb", "#0f766e", "#be123c", "#c2410c"],
    )
    fig_segmento.update_traces(hovertemplate="%{x}<br>Ventas: %{y:$,.2f}<extra></extra>")
    style_figure(fig_segmento, 350)

    fig_trimestre = go.Figure()
    fig_trimestre.add_trace(
        go.Bar(
            x=ventas_trimestre["Trimestre"],
            y=ventas_trimestre["Monto_Neto"],
            marker_color="#23313d",
            hovertemplate="Trimestre %{x}<br>Ventas: %{y:$,.2f}<extra></extra>",
        )
    )
    fig_trimestre.update_layout(title="Ventas por trimestre", xaxis_title="Trimestre", yaxis_title="Ventas netas")
    style_figure(fig_trimestre, 350)

    top_categoria = ventas_categoria.iloc[0]
    top_pais = top_paises.iloc[0]
    top_producto = top_productos.iloc[0]
    top_segmento = ventas_segmento.iloc[0]

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Informe Modelo Estrella - Ventas</title>
  <style>
    :root {{
      --ink: #1d2730;
      --muted: #687583;
      --line: #dce3ea;
      --panel: #ffffff;
      --wash: #f5f7fa;
      --teal: #0f766e;
      --blue: #2563eb;
      --orange: #c2410c;
      --purple: #7c3aed;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--wash);
      color: var(--ink);
      font-family: "Segoe UI", Arial, sans-serif;
      line-height: 1.45;
    }}
    header {{
      background: #10202a;
      color: white;
      padding: 34px 28px 24px;
      border-bottom: 6px solid var(--teal);
    }}
    .wrap {{ width: min(1240px, calc(100% - 40px)); margin: 0 auto; }}
    .eyebrow {{ color: #8bd8cf; font-size: 13px; text-transform: uppercase; letter-spacing: .08em; font-weight: 700; }}
    h1 {{ margin: 6px 0 8px; font-size: clamp(30px, 5vw, 52px); line-height: 1.05; letter-spacing: 0; }}
    h2 {{ margin: 0 0 16px; font-size: 23px; letter-spacing: 0; }}
    h3 {{ margin: 0 0 8px; font-size: 16px; letter-spacing: 0; }}
    p {{ margin: 0; }}
    .subtitle {{ max-width: 860px; color: #d6e1e8; font-size: 17px; }}
    main {{ padding: 24px 0 36px; }}
    section {{ margin-top: 22px; }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
    }}
    .kpi, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(16, 32, 42, .06);
    }}
    .kpi {{ padding: 17px 18px; min-height: 112px; }}
    .kpi span {{ display: block; color: var(--muted); font-size: 13px; font-weight: 700; text-transform: uppercase; }}
    .kpi strong {{ display: block; margin-top: 8px; font-size: clamp(21px, 3vw, 30px); line-height: 1.1; }}
    .kpi small {{ display: block; margin-top: 8px; color: var(--muted); }}
    .grid-2 {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .grid-3 {{ display: grid; grid-template-columns: 1.2fr .8fr; gap: 16px; }}
    .panel {{ padding: 18px; overflow: hidden; }}
    .insights {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}
    .insight {{
      border-left: 4px solid var(--teal);
      background: white;
      border-radius: 8px;
      border-top: 1px solid var(--line);
      border-right: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      padding: 15px;
      min-height: 118px;
    }}
    .insight:nth-child(2) {{ border-left-color: var(--blue); }}
    .insight:nth-child(3) {{ border-left-color: var(--orange); }}
    .insight:nth-child(4) {{ border-left-color: var(--purple); }}
    .insight strong {{ display: block; margin-bottom: 6px; }}
    .insight span {{ color: var(--muted); }}
    .model {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
    }}
    .table-card {{
      background: #f9fbfc;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 13px;
    }}
    .table-card strong {{ display: block; font-size: 14px; margin-bottom: 6px; }}
    .table-card span {{ display: block; color: var(--muted); font-size: 13px; }}
    footer {{ color: var(--muted); padding: 18px 0 0; font-size: 13px; }}
    @media (max-width: 980px) {{
      .kpis, .insights, .grid-2, .grid-3, .model {{ grid-template-columns: 1fr; }}
      header {{ padding-left: 0; padding-right: 0; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="eyebrow">Modelo estrella de ventas</div>
      <h1>Informe ejecutivo de ventas</h1>
      <p class="subtitle">Análisis integrado de hechos de venta y dimensiones de cliente, producto, tiempo y vendedor. Incluye indicadores clave, visuales interactivos y hallazgos principales.</p>
    </div>
  </header>
  <main class="wrap">
    <section class="kpis">
      <div class="kpi"><span>Total ventas netas</span><strong>{money(total_ventas)}</strong><small>Después de descuentos</small></div>
      <div class="kpi"><span>Transacciones</span><strong>{number(transacciones)}</strong><small>Ticket promedio: {money(ticket_promedio)}</small></div>
      <div class="kpi"><span>Clientes activos</span><strong>{number(clientes)}</strong><small>{number(productos)} productos vendidos</small></div>
      <div class="kpi"><span>Descuento aplicado</span><strong>{money(total_descuentos)}</strong><small>{pct(descuento_pct)} del monto bruto</small></div>
    </section>

    <section>
      <h2>Hallazgos principales</h2>
      <div class="insights">
        <div class="insight"><strong>Categoría líder</strong><span>{top_categoria["Categoría"]} concentra {money(top_categoria["Monto_Neto"])} en ventas netas.</span></div>
        <div class="insight"><strong>País con mayor venta</strong><span>{top_pais["País"]} lidera el ranking geográfico con {money(top_pais["Monto_Neto"])}.</span></div>
        <div class="insight"><strong>Producto estrella</strong><span>{top_producto["Nombre_Producto"]} es el producto de mayor facturación: {money(top_producto["Monto_Neto"])}.</span></div>
        <div class="insight"><strong>Segmento clave</strong><span>{top_segmento["Segmento"]} es el segmento con mejor desempeño comercial.</span></div>
      </div>
    </section>

    <section class="grid-2">
      <div class="panel">{chart_html(fig_categoria, include_js=True)}</div>
      <div class="panel">{chart_html(fig_paises)}</div>
    </section>

    <section class="grid-3">
      <div class="panel">{chart_html(fig_tiempo)}</div>
      <div class="panel">{chart_html(fig_region)}</div>
    </section>

    <section class="grid-2">
      <div class="panel">{chart_html(fig_productos)}</div>
      <div class="panel">{chart_html(fig_descuentos)}</div>
    </section>

    <section class="grid-2">
      <div class="panel">{chart_html(fig_segmento)}</div>
      <div class="panel">{chart_html(fig_trimestre)}</div>
    </section>

    <section>
      <h2>Estructura del modelo estrella</h2>
      <div class="model">
        <div class="table-card"><strong>Fact_Ventas</strong><span>{number(len(fact))} registros</span><span>Cantidad, monto bruto, descuento y monto neto</span></div>
        <div class="table-card"><strong>Dim_Cliente</strong><span>{number(len(cliente))} registros</span><span>Cliente, país y segmento</span></div>
        <div class="table-card"><strong>Dim_Producto</strong><span>{number(len(producto))} registros</span><span>Producto, categoría y precio</span></div>
        <div class="table-card"><strong>Dim_Tiempo</strong><span>{number(len(tiempo))} registros</span><span>Fecha, mes, año y trimestre</span></div>
        <div class="table-card"><strong>Dim_Vendedor</strong><span>{number(len(vendedor))} registros</span><span>Vendedor y región</span></div>
      </div>
    </section>

    <footer>Informe generado el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} desde {EXCEL_PATH.name}.</footer>
  </main>
</body>
</html>"""

    OUTPUT_PATH.write_text(html, encoding="utf-8")
    return OUTPUT_PATH


if __name__ == "__main__":
    print(build_report())
