# 📊 Dashboard Modelo Estrella - Guía de Uso

## ✅ Descripción General

Se ha generado exitosamente un **Dashboard interactivo** basado en el modelo estrella de ventas con **8 gráficos principales**.

**Datos incluidos:**
- 💰 **Total Ventas**: $92,111,647.87
- 👥 **Clientes Únicos**: 200
- 📦 **Productos**: 30
- 📈 **Transacciones**: 50,000

---

## 📂 Estructura de Archivos

```
graficos/
├── index.html                    # Dashboard principal (ABRE ESTE)
├── 01_ventas_categoria.html      # Ventas por Categoría de Producto
├── 02_top_paises.html            # Top 10 Países por Ventas
├── 03_ventas_tiempo.html         # Ventas a lo Largo del Tiempo
├── 04_ventas_region.html         # Distribución de Ventas por Región
├── 05_top_productos.html         # Top 10 Productos
├── 06_descuentos_ventas.html     # Descuentos vs Ventas Netas
├── 07_ventas_segmento.html       # Ventas por Segmento de Cliente
└── 08_cantidad_monto.html        # Cantidad vs Monto por Producto
```

---

## 🚀 Cómo Usar el Dashboard

### Opción 1: Abrir desde el navegador
1. Ve a la carpeta `graficos/`
2. Haz doble clic en `index.html`
3. El navegador abrirá el dashboard principal

### Opción 2: Abrir desde VS Code
1. Haz clic derecho en `index.html`
2. Selecciona "Open with Live Server" (si tienes la extensión instalada)

---

## 📊 Descripción de los Gráficos

### 1. **💼 Ventas por Categoría**
- **Tipo**: Gráfico de barras vertical
- **Datos**: Ventas totales agrupadas por categoría de producto
- **Uso**: Identificar qué categorías generan más ingresos

### 2. **🌍 Top 10 Países**
- **Tipo**: Gráfico de barras horizontal
- **Datos**: Los 10 países con mayor volumen de ventas
- **Uso**: Análisis geográfico de desempeño

### 3. **📅 Ventas en el Tiempo**
- **Tipo**: Gráfico de línea con marcadores
- **Datos**: Ventas agregadas por mes
- **Uso**: Ver tendencias y patrones estacionales

### 4. **🗺️ Ventas por Región**
- **Tipo**: Gráfico circular (pie chart)
- **Datos**: Distribución de ventas por región de vendedor
- **Uso**: Proporciones de ventas por cada región

### 5. **🏆 Top 10 Productos**
- **Tipo**: Gráfico de barras horizontal
- **Datos**: Los 10 productos más vendidos (por monto)
- **Uso**: Identificar productos estrella

### 6. **💹 Descuentos vs Ventas**
- **Tipo**: Gráfico de dispersión (scatter)
- **Datos**: Relación entre descuentos aplicados y ventas netas
- **Tamaño de burbuja**: Cantidad vendida
- **Uso**: Analizar el impacto de descuentos

### 7. **👤 Ventas por Segmento**
- **Tipo**: Gráfico de barras vertical
- **Datos**: Ventas totales por segmento de cliente
- **Uso**: Identificar qué segmentos más venden

### 8. **📊 Cantidad vs Monto**
- **Tipo**: Gráfico de barras agrupadas
- **Datos**: Top 10 productos con cantidad vendida y monto
- **Uso**: Comparar volumen vs ingresos

---

## 🔄 Características Interactivas

Todos los gráficos de Plotly incluyen:
- ✅ **Zoom**: Haz clic y arrastra para zoom en áreas específicas
- ✅ **Pan**: Mantén presionado Shift y arrastra para mover
- ✅ **Hover**: Pasa el mouse para ver valores exactos
- ✅ **Leyenda**: Haz clic en los elementos de la leyenda para mostrar/ocultar series
- ✅ **Descarga**: Botón de cámara (📸) para descargar como PNG

---

## 📈 Datos del Modelo Estrella

El dashboard se basa en **4 dimensiones y 1 tabla de hechos**:

### Dimensiones:
- **Dim_Cliente**: ID, Nombre, País, Segmento
- **Dim_Producto**: ID, Nombre, Categoría, Precio Unitario
- **Dim_Tiempo**: Fecha, Año, Mes, Trimestre
- **Dim_Vendedor**: ID, Nombre, Región

### Tabla de Hechos:
- **Fact_Ventas**: Cantidad, Monto Bruto, Descuento, Monto Neto

---

## 🛠️ Mantenimiento

### Actualizar los gráficos
Si actualizas el archivo `modelo_estrella_ventas.xlsx`, ejecuta:

```bash
python app.py
```

Esto regenerará todos los gráficos automáticamente.

### Estructura del código
- **app.py**: Script principal que genera los gráficos
- **requirements.txt**: Dependencias Python necesarias

---

## 💡 Tips Útiles

1. **Para análisis profundos**: Abre cada gráfico individual para obtener una vista más grande y detallada
2. **Para presentaciones**: Captura pantallazos de los gráficos o descárgalos como imágenes PNG
3. **Para reportes**: Exporta los gráficos y úsalos en Word, PowerPoint o PDF
4. **Para compartir**: Comparte toda la carpeta `graficos/` para que otros vean el dashboard

---

## 📝 Medidas DAX Creadas en Power BI

Además del dashboard HTML, se han creado las siguientes medidas en tu modelo Power BI:

- `Total Ventas` = SUMX(Fact_Ventas, Fact_Ventas[Monto_Neto])
- `Total Cantidad` = SUM(Fact_Ventas[Cantidad])
- `Total Bruto` = SUMX(Fact_Ventas, Fact_Ventas[Monto_Bruto])
- `Total Descuentos` = SUMX(Fact_Ventas, Fact_Ventas[Descuento])
- `Promedio por Unidad` = DIVIDE([Total Ventas], [Total Cantidad], 0)
- `Cantidad Clientes` = DISTINCTCOUNT(Fact_Ventas[ID_Cliente])
- `Cantidad Productos` = DISTINCTCOUNT(Fact_Ventas[ID_Producto])
- `Total Transacciones` = DISTINCTCOUNT(Fact_Ventas[ID_Venta])
- `Venta Promedio` = DIVIDE([Total Ventas], [Total Transacciones], 0)
- `% Descuento` = DIVIDE([Total Descuentos], [Total Bruto])

---

## 🎓 Conclusión

Ahora tienes:
✅ Un **modelo de datos estrella** bien estructurado en Power BI
✅ **10 medidas DAX** listas para usar
✅ Un **dashboard HTML interactivo** con 8 gráficos
✅ **Gráficos individuales** para análisis detallado

¡Listo para presentar tus análisis de ventas! 📊
