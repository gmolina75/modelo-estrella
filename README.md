# 📊 Modelo Estrella de Ventas — Guía de Power BI

Este repositorio contiene un modelo de datos en estrella para el análisis de ventas, implementado en **Power BI Desktop** a partir de un archivo de Excel.

El artefacto principal es el proyecto Power BI (`modeloEstrella.pbip` / `modeloEstrella.pbix`), que contiene la ingesta, las relaciones del modelo estrella, las medidas DAX y los visuales de reporte.

> **⚠️ Dato clave:** este modelo se construyó cargando el archivo de Excel **`modelo_estrella_ventas.xlsx`** en Power BI Desktop a través del archivo **`modeloEstrella.pbix`**.

---

## ✅ Alcance del modelo

- **Fuente de datos:** `modelo_estrella_ventas.xlsx`
- **Total Ventas Netas:** ~USD 92,1 millones
- **Clientes únicos:** 200
- **Productos:** 30
- **Transacciones:** 50.000
- **Período:** datos diarios agregados por año, mes, trimestre y día

---

## 📂 Archivos principales de Power BI

```
.
├── modeloEstrella.pbip                         # Proyecto de Power BI (PBIP)
├── modeloEstrella.pbix                         # Archivo binario de Power BI Desktop
├── modeloEstrella.Report/                      # Definición del informe (PBIP)
│   ├── definition.pbir
│   └── definition/
│       ├── report.json
│       └── pages/...
├── modeloEstrella.SemanticModel/               # Modelo semántico (TOM/DAX)
│   ├── definition.pbism
│   ├── definition/model.tmdl
│   ├── definition/relationships.tmdl
│   └── definition/tables/*.tmdl
└── modelo_estrella_ventas.xlsx                 # Origen de datos en Excel
```

> Los archivos bajo `.pbi/` y `cache.abf` son generados por Power BI Desktop y están ignorados en el control de versiones.

---

## 🔄 Ingesta de datos desde Excel

Power BI importa los datos directamente desde la hoja de Excel mediante el conector **Excel.Workbook**. Cada tabla del modelo apunta a una hoja del archivo:

| Tabla en Power BI | Hoja de Excel | Descripción |
|-------------------|---------------|-------------|
| `Fact_Ventas`     | `Fact_Ventas` | Tabla de hechos con las transacciones |
| `Dim_Cliente`     | `Dim_Cliente` | Dimensión de clientes |
| `Dim_Producto`    | `Dim_Producto`| Dimensión de productos |
| `Dim_Tiempo`      | `Dim_Tiempo`  | Dimensión de tiempo/calendario |
| `Dim_Vendedor`    | `Dim_Vendedor`| Dimensión de vendedores |

### Consideraciones importantes

- El modelo usa **modo Import**: los datos se cargan en memoria al abrir el archivo `.pbip` / `.pbix`.
- Las expresiones M de las particiones referencian la ruta absoluta del archivo Excel. Si mueves el proyecto a otra ubicación, deberás actualizar la ruta en Power BI Desktop mediante **Transformar datos → Configuración de origen de datos**.
- Si se actualiza el contenido del Excel (nuevas filas, productos o clientes), basta con hacer clic en **Inicio → Actualizar** para recargar todo el modelo.

---

## 🏗️ Modelo de datos estrella

### Tabla de hechos

**`Fact_Ventas`**

| Columna       | Tipo   | Descripción |
|---------------|--------|-------------|
| `ID_Venta`    | Entero | Identificador único de la transacción |
| `ID_Tiempo`   | Entero | Clave foránea a `Dim_Tiempo` |
| `ID_Producto` | Entero | Clave foránea a `Dim_Producto` |
| `ID_Cliente`  | Entero | Clave foránea a `Dim_Cliente` |
| `ID_Vendedor` | Entero | Clave foránea a `Dim_Vendedor` |
| `Cantidad`    | Entero | Unidades vendidas |
| `Monto_Bruto` | Decimal| Ingreso antes de descuentos |
| `Descuento`   | Decimal| Monto descontado |
| `Monto_Neto`  | Decimal| Ingreso final (ventas netas) |

### Dimensiones

| Dimensión       | Columnas principales |
|-----------------|----------------------|
| `Dim_Cliente`   | `ID_Cliente`, `Nombre_Cliente`, `País`, `Segmento` |
| `Dim_Producto`  | `ID_Producto`, `Nombre_Producto`, `Categoría`, `Precio_Unitario` |
| `Dim_Tiempo`    | `ID_Tiempo`, `Fecha`, `Año`, `Mes`, `Día`, `Trimestre` |
| `Dim_Vendedor`  | `ID_Vendedor`, `Nombre_Vendedor`, `Región` |

### Relaciones

El modelo define las siguientes relaciones de uno a muchos entre dimensiones y la tabla de hechos:

- `Dim_Cliente.ID_Cliente` → `Fact_Ventas.ID_Cliente`
- `Dim_Producto.ID_Producto` → `Fact_Ventas.ID_Producto`
- `Dim_Tiempo.ID_Tiempo` → `Fact_Ventas.ID_Tiempo`
- `Dim_Vendedor.ID_Vendedor` → `Fact_Ventas.ID_Vendedor`

---

## 📈 Medidas DAX implementadas

Las siguientes medidas han sido creadas en la tabla `Fact_Ventas`:

| Medida | Fórmula DAX | Descripción |
|--------|-------------|-------------|
| **Total Ventas** | `SUMX(Fact_Ventas, Fact_Ventas[Monto_Neto])` | Suma de ventas netas |
| **Total Cantidad** | `SUM(Fact_Ventas[Cantidad])` | Total de unidades vendidas |
| **Total Bruto** | `SUMX(Fact_Ventas, Fact_Ventas[Monto_Bruto])` | Suma de ventas brutas |
| **Total Descuentos** | `SUMX(Fact_Ventas, Fact_Ventas[Descuento])` | Suma de descuentos aplicados |
| **Promedio por Unidad** | `DIVIDE([Total Ventas], [Total Cantidad], 0)` | Ingreso neto promedio por unidad vendida |
| **Total Transacciones** | `DISTINCTCOUNT(Fact_Ventas[ID_Venta])` | Cantidad de transacciones únicas |
| **Venta Promedio** | `DIVIDE([Total Ventas], [Total Transacciones], 0)` | Valor promedio por transacción |
| **% Descuento** | `DIVIDE([Total Descuentos], [Total Bruto])` | Porcentaje de descuento sobre el bruto |
| **Cantidad Clientes** | `DISTINCTCOUNT(Fact_Ventas[ID_Cliente])` | Número de clientes únicos con ventas |
| **Cantidad Productos** | `DISTINCTCOUNT(Fact_Ventas[ID_Producto])` | Número de productos vendidos |

---

## 🚀 Cómo abrir y usar el modelo

### Opción 1: Power BI Desktop

1. Abre **Power BI Desktop**.
2. Selecciona **Archivo → Abrir → Examinar**.
3. Abre `modeloEstrella.pbip` (formato de proyecto) o `modeloEstrella.pbix` (archivo binario).
4. Si se solicita, actualiza la ruta del origen de datos apuntando a `modelo_estrella_ventas.xlsx`.
5. Usa el panel **Datos**, **Modelo** y **Informe** para explorar tablas, relaciones y visuales.

### Opción 2: Actualizar datos después de cambiar el Excel

1. Edita o reemplaza `modelo_estrella_ventas.xlsx`.
2. En Power BI Desktop, ve a **Inicio → Actualizar**.
3. Verifica que las medidas y visuales reflejen los nuevos valores.

---

## 🛠️ Mantenimiento y modificaciones

Si se cambian columnas o nombres de hojas en el archivo Excel, también es necesario actualizar:

1. Las expresiones M en `modeloEstrella.SemanticModel/definition/tables/*.tmdl`.
2. Las referencias a columnas en las medidas DAX.
3. Los visuales del informe en `modeloEstrella.Report/definition/pages/`.

Para modificar el modelo de forma programática también puedes ejecutar:

```bash
python generar_visuales_pbip.py
```

Este script regenera las definiciones JSON de los visuales del reporte a partir del modelo semántico existente.

---

## 📤 Publicación

Para compartir el dashboard:

1. Abre `modeloEstrella.pbix` en Power BI Desktop.
2. Selecciona **Inicio → Publicar**.
3. Inicia sesión en el servicio de Power BI y elige el área de trabajo de destino.

---

## 📝 Notas

- El proyecto incluye scripts auxiliares de Python (`app.py`, `generar_informe.py`, `generar_visuales_pbip.py`) para generar gráficos HTML y visuales PBIP. Estos no son necesarios para usar el modelo en Power BI Desktop, pero facilitan la generación de artefactos adicionales.
- Los datos del Excel son de ejemplo/sintéticos. Verifica su contenido antes de publicar en entornos reales.
