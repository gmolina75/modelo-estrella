import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Configurar salida estándar en UTF-8 para evitar errores de codificación en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ============================================
# CARGAR DATOS
# ============================================
def load_data():
    """Carga todos los datos desde el Excel"""
    file_path = "modelo_estrella_ventas.xlsx"
    
    # Leer todas las hojas
    dim_cliente = pd.read_excel(file_path, sheet_name="Dim_Cliente")
    dim_producto = pd.read_excel(file_path, sheet_name="Dim_Producto")
    dim_tiempo = pd.read_excel(file_path, sheet_name="Dim_Tiempo")
    dim_vendedor = pd.read_excel(file_path, sheet_name="Dim_Vendedor")
    fact_ventas = pd.read_excel(file_path, sheet_name="Fact_Ventas")
    
    # Convertir tipos de datos
    dim_tiempo["Fecha"] = pd.to_datetime(dim_tiempo["Fecha"])
    fact_ventas["Monto_Neto"] = pd.to_numeric(fact_ventas["Monto_Neto"], errors="coerce")
    fact_ventas["Monto_Bruto"] = pd.to_numeric(fact_ventas["Monto_Bruto"], errors="coerce")
    fact_ventas["Descuento"] = pd.to_numeric(fact_ventas["Descuento"], errors="coerce")
    fact_ventas["Cantidad"] = pd.to_numeric(fact_ventas["Cantidad"], errors="coerce")
    
    return dim_cliente, dim_producto, dim_tiempo, dim_vendedor, fact_ventas

# ============================================
# CREAR TABLA CONSOLIDADA
# ============================================
def merge_data(dim_cliente, dim_producto, dim_tiempo, dim_vendedor, fact_ventas):
    """Consolida todas las dimensiones con los hechos"""
    df = fact_ventas.copy()
    
    # Merge con dimensiones
    df = df.merge(dim_cliente[["ID_Cliente", "Nombre_Cliente", "País", "Segmento"]], 
                  on="ID_Cliente", how="left")
    df = df.merge(dim_producto[["ID_Producto", "Nombre_Producto", "Categoría", "Precio_Unitario"]], 
                  on="ID_Producto", how="left")
    df = df.merge(dim_tiempo[["ID_Tiempo", "Fecha", "Año", "Mes", "Trimestre"]], 
                  on="ID_Tiempo", how="left")
    df = df.merge(dim_vendedor[["ID_Vendedor", "Nombre_Vendedor", "Región"]], 
                  on="ID_Vendedor", how="left")
    
    return df

# ============================================
# GENERAR GRÁFICOS
# ============================================
def create_dashboard():
    """Crea todos los gráficos del dashboard"""
    
    print("📊 Cargando datos...")
    dim_cliente, dim_producto, dim_tiempo, dim_vendedor, fact_ventas = load_data()
    df_consolidado = merge_data(dim_cliente, dim_producto, dim_tiempo, dim_vendedor, fact_ventas)
    
    # Crear carpeta para gráficos
    if not os.path.exists("graficos"):
        os.makedirs("graficos")
    
    # ============================================
    # GRÁFICO 1: Ventas por Categoría
    # ============================================
    print("📈 Generando gráfico 1: Ventas por Categoría...")
    ventas_categoria = df_consolidado.groupby("Categoría")["Monto_Neto"].sum().sort_values(ascending=False)
    fig1 = px.bar(
        x=ventas_categoria.index,
        y=ventas_categoria.values,
        labels={"x": "Categoría", "y": "Ventas ($)"},
        title="Ventas por Categoría de Producto",
        color=ventas_categoria.values,
        color_continuous_scale="Blues"
    )
    fig1.update_layout(height=500, showlegend=False)
    fig1.write_html("graficos/01_ventas_categoria.html")
    
    # ============================================
    # GRÁFICO 2: Top 10 Países por Ventas
    # ============================================
    print("📈 Generando gráfico 2: Top 10 Países...")
    ventas_pais = df_consolidado.groupby("País")["Monto_Neto"].sum().sort_values(ascending=False).head(10)
    fig2 = px.bar(
        x=ventas_pais.values,
        y=ventas_pais.index,
        orientation="h",
        labels={"x": "Ventas ($)", "y": "País"},
        title="Top 10 Países por Ventas",
        color=ventas_pais.values,
        color_continuous_scale="Greens"
    )
    fig2.update_layout(height=500, showlegend=False)
    fig2.write_html("graficos/02_top_paises.html")
    
    # ============================================
    # GRÁFICO 3: Ventas a lo Largo del Tiempo
    # ============================================
    print("📈 Generando gráfico 3: Ventas en el Tiempo...")
    ventas_tiempo = df_consolidado.groupby(df_consolidado["Fecha"].dt.to_period("M"))["Monto_Neto"].sum()
    ventas_tiempo.index = ventas_tiempo.index.to_timestamp()
    fig3 = px.line(
        x=ventas_tiempo.index,
        y=ventas_tiempo.values,
        markers=True,
        labels={"x": "Fecha", "y": "Ventas ($)"},
        title="Ventas a lo Largo del Tiempo"
    )
    fig3.update_traces(line=dict(color="#667eea", width=3), marker=dict(size=8))
    fig3.update_layout(height=500, hovermode="x unified")
    fig3.write_html("graficos/03_ventas_tiempo.html")
    
    # ============================================
    # GRÁFICO 4: Distribución por Región
    # ============================================
    print("📈 Generando gráfico 4: Distribución por Región...")
    ventas_region = df_consolidado.groupby("Región")["Monto_Neto"].sum()
    fig4 = px.pie(
        values=ventas_region.values,
        names=ventas_region.index,
        title="Distribución de Ventas por Región",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig4.update_layout(height=500)
    fig4.write_html("graficos/04_ventas_region.html")
    
    # ============================================
    # GRÁFICO 5: Top 10 Productos
    # ============================================
    print("📈 Generando gráfico 5: Top 10 Productos...")
    top_productos = df_consolidado.groupby("Nombre_Producto")["Monto_Neto"].sum().sort_values(ascending=False).head(10)
    fig5 = px.bar(
        x=top_productos.values,
        y=top_productos.index,
        orientation="h",
        labels={"x": "Ventas ($)", "y": "Producto"},
        title="Top 10 Productos",
        color=top_productos.values,
        color_continuous_scale="Reds"
    )
    fig5.update_layout(height=500, showlegend=False)
    fig5.write_html("graficos/05_top_productos.html")
    
    # ============================================
    # GRÁFICO 6: Descuentos vs Ventas Netas
    # ============================================
    print("📈 Generando gráfico 6: Descuentos vs Ventas...")
    df_scatter = df_consolidado.groupby("Nombre_Producto").agg({
        "Descuento": "sum",
        "Monto_Neto": "sum",
        "Cantidad": "sum"
    }).reset_index()
    
    fig6 = px.scatter(
        df_scatter,
        x="Descuento",
        y="Monto_Neto",
        size="Cantidad",
        hover_name="Nombre_Producto",
        title="Descuentos vs Ventas Netas",
        labels={"Descuento": "Total Descuentos ($)", "Monto_Neto": "Ventas Netas ($)"},
        color_discrete_sequence=["#764ba2"]
    )
    fig6.update_layout(height=500)
    fig6.write_html("graficos/06_descuentos_ventas.html")
    
    # ============================================
    # GRÁFICO 7: Ventas por Segmento de Cliente
    # ============================================
    print("📈 Generando gráfico 7: Ventas por Segmento...")
    ventas_segmento = df_consolidado.groupby("Segmento")["Monto_Neto"].sum().sort_values(ascending=False)
    fig7 = px.bar(
        x=ventas_segmento.index,
        y=ventas_segmento.values,
        labels={"x": "Segmento", "y": "Ventas ($)"},
        title="Ventas por Segmento de Cliente",
        color=ventas_segmento.values,
        color_continuous_scale="Purples"
    )
    fig7.update_layout(height=500, showlegend=False)
    fig7.write_html("graficos/07_ventas_segmento.html")
    
    # ============================================
    # GRÁFICO 8: Cantidad Vendida vs Monto por Producto
    # ============================================
    print("📈 Generando gráfico 8: Cantidad vs Monto...")
    df_producto_stats = df_consolidado.groupby("Nombre_Producto").agg({
        "Cantidad": "sum",
        "Monto_Neto": "sum"
    }).reset_index().sort_values("Monto_Neto", ascending=False).head(10)
    
    fig8 = px.bar(
        df_producto_stats,
        x="Nombre_Producto",
        y=["Cantidad", "Monto_Neto"],
        barmode="group",
        title="Top 10: Cantidad vs Monto por Producto",
        labels={"Nombre_Producto": "Producto", "value": "Valor"}
    )
    fig8.update_layout(height=500, hovermode="x")
    fig8.write_html("graficos/08_cantidad_monto.html")
    
    # ============================================
    # RESUMEN - CREAR ÍNDICE HTML
    # ============================================
    print("📄 Generando índice HTML...")
    
    html_index = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Modelo Estrella - Ventas</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            header {{ background: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center; }}
            header h1 {{ color: #667eea; margin-bottom: 10px; font-size: 2.5em; }}
            header p {{ color: #666; font-size: 1.1em; }}
            .kpi-section {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .kpi-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center; }}
            .kpi-card h3 {{ color: #667eea; font-size: 0.9em; margin-bottom: 10px; text-transform: uppercase; }}
            .kpi-card .value {{ font-size: 2em; font-weight: bold; color: #333; }}
            .graphs-section {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .graph-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; }}
            .graph-card h3 {{ color: #667eea; margin-bottom: 15px; font-size: 1.1em; }}
            .graph-card a {{ display: inline-block; width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; text-align: center; transition: transform 0.2s; font-weight: bold; }}
            .graph-card a:hover {{ transform: scale(1.05); }}
            footer {{ background: white; padding: 20px; border-radius: 10px; text-align: center; color: #666; margin-top: 30px; }}
            .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; background: white; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
            .info-item {{ text-align: center; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
            .info-item strong {{ color: #667eea; font-size: 1.2em; display: block; margin-bottom: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📊 Dashboard Modelo Estrella</h1>
                <p>Análisis completo de ventas con dimensiones de Cliente, Producto, Tiempo y Vendedor</p>
            </header>
            
            <div class="info-grid">
                <div class="info-item">
                    <strong>💰 Total Ventas</strong>
                    <span>${0:,.2f}</span>
                </div>
                <div class="info-item">
                    <strong>👥 Clientes Únicos</strong>
                    <span>{1:,}</span>
                </div>
                <div class="info-item">
                    <strong>📦 Productos</strong>
                    <span>{2:,}</span>
                </div>
                <div class="info-item">
                    <strong>📈 Transacciones</strong>
                    <span>{3:,}</span>
                </div>
            </div>
            
            <div class="graphs-section">
                <div class="graph-card">
                    <h3>💼 Ventas por Categoría</h3>
                    <a href="01_ventas_categoria.html" target="_blank">Ver Gráfico Interactivo</a>
                </div>
                
                <div class="graph-card">
                    <h3>🌍 Top 10 Países</h3>
                    <a href="02_top_paises.html" target="_blank">Ver Gráfico Interactivo</a>
                </div>
                
                <div class="graph-card">
                    <h3>📅 Ventas en el Tiempo</h3>
                    <a href="03_ventas_tiempo.html" target="_blank">Ver Gráfico Interactivo</a>
                </div>
                
                <div class="graph-card">
                    <h3>🗺️ Ventas por Región</h3>
                    <a href="04_ventas_region.html" target="_blank">Ver Gráfico Interactivo</a>
                </div>
                
                <div class="graph-card">
                    <h3>🏆 Top 10 Productos</h3>
                    <a href="05_top_productos.html" target="_blank">Ver Gráfico Interactivo</a>
                </div>
                
                <div class="graph-card">
                    <h3>💹 Descuentos vs Ventas</h3>
                    <a href="06_descuentos_ventas.html" target="_blank">Ver Gráfico Interactivo</a>
                </div>
                
                <div class="graph-card">
                    <h3>👤 Ventas por Segmento</h3>
                    <a href="07_ventas_segmento.html" target="_blank">Ver Gráfico Interactivo</a>
                </div>
                
                <div class="graph-card">
                    <h3>📊 Cantidad vs Monto</h3>
                    <a href="08_cantidad_monto.html" target="_blank">Ver Gráfico Interactivo</a>
                </div>
            </div>
            
            <footer>
                <p>Dashboard generado el {4}</p>
                <p>Modelo Estrella - Análisis de Ventas | Dimensiones: Cliente, Producto, Tiempo, Vendedor</p>
            </footer>
        </div>
    </body>
    </html>
    """.format(
        df_consolidado["Monto_Neto"].sum(),
        df_consolidado["ID_Cliente"].nunique(),
        df_consolidado["ID_Producto"].nunique(),
        df_consolidado["ID_Venta"].nunique(),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    with open("graficos/index.html", "w", encoding="utf-8") as f:
        f.write(html_index)
    
    print("\n✅ ¡Dashboard completado!")
    print(f"📁 Gráficos guardados en: {os.path.abspath('graficos')}")
    print(f"🌐 Abre: {os.path.abspath('graficos/index.html')}")

if __name__ == "__main__":
    create_dashboard()
