# Guía para Agentes de Código — Modelo Estrella de Ventas

> Este archivo resume la arquitectura, convenciones y comandos útiles para trabajar en este proyecto. El lector se asume sin conocimiento previo del mismo.

---

## 1. Descripción general del proyecto

Este repositorio contiene un **dashboard interactivo de ventas** construido a partir de un **modelo estrella** de datos. El flujo de trabajo es:

1. Los datos viven en una hoja de Excel (`modelo_estrella_ventas.xlsx`).
2. Scripts de Python leen el Excel, unen las dimensiones con la tabla de hechos y generan visualizaciones HTML con Plotly.
3. Existe un modelo de Power BI en formato PBIP (`modeloEstrella.pbip`) que apunta al mismo archivo Excel y define medidas DAX y visuales.

> **Dato clave:** el modelo principal de Power BI se construyó cargando **`modelo_estrella_ventas.xlsx`** en **`modeloEstrella.pbix`**.

El proyecto no es una aplicación web servidor/cliente. Los artefactos finales son **archivos HTML estáticos** y un **archivo Power BI**.

### Datos principales (actualmente)

- Total Ventas Netas: ~USD 92,1 millones
- Clientes únicos: 200
- Productos: 30
- Transacciones: 50.000

### Modelo de datos

- **Tabla de hechos:** `Fact_Ventas` (Cantidad, Monto_Bruto, Descuento, Monto_Neto)
- **Dimensiones:**
  - `Dim_Cliente` (ID_Cliente, Nombre_Cliente, País, Segmento)
  - `Dim_Producto` (ID_Producto, Nombre_Producto, Categoría, Precio_Unitario)
  - `Dim_Tiempo` (ID_Tiempo, Fecha, Año, Mes, Día, Trimestre)
  - `Dim_Vendedor` (ID_Vendedor, Nombre_Vendedor, Región)

---

## 2. Estructura de archivos

```
.
├── README.md                          # Guía de uso en español
├── requirements.txt                   # Dependencias de Python
├── app.py                             # Generador principal del dashboard HTML
├── generar_informe.py                 # Generador de informe ejecutivo HTML
├── generar_visuales_pbip.py           # Generador de visuales JSON para el PBIP
├── modelo_estrella_ventas.xlsx        # Fuente de datos principal
├── modeloEstrella.pbip                # Archivo de proyecto de Power BI (PBIP)
├── modeloEstrella.pbix                # Archivo binario de Power BI Desktop
├── modeloEstrella.Report/             # Definición del informe (formato PBIP)
│   ├── definition.pbir
│   ├── definition/report.json
│   └── definition/pages/...
├── modeloEstrella.SemanticModel/      # Definición del modelo semántico (TOM/DAX)
│   ├── definition.pbism
│   ├── definition/model.tmdl
│   ├── definition/relationships.tmdl
│   └── definition/tables/*.tmdl
└── graficos/                          # Salida generada (HTML)
    ├── index.html                     # Dashboard principal
    ├── informe_modelo_estrella.html   # Informe ejecutivo
    ├── 01_ventas_categoria.html
    ├── 02_top_paises.html
    ├── 03_ventas_tiempo.html
    ├── 04_ventas_region.html
    ├── 05_top_productos.html
    ├── 06_descuentos_ventas.html
    ├── 07_ventas_segmento.html
    └── 08_cantidad_monto.html
```

---

## 3. Stack tecnológico

- **Lenguaje:** Python 3.14.4 (versión observada en el entorno)
- **Librerías principales:**
  - `pandas` — manipulación de datos
  - `openpyxl` — lectura de archivos Excel
  - `plotly` (express + graph_objects) — generación de gráficos interactivos
  - `numpy` — dependencia transitiva/usos numéricos
- **Visualización adicional:** Power BI Desktop (archivos `.pbip` / `.pbix`)
- **Fuente de datos:** Excel 2007+ (`.xlsx`)

No se utilizan frameworks web, bases de datos, ni herramientas de empaquetado como `pyproject.toml`, `setup.py` o `package.json`.

---

## 4. Cómo ejecutar el proyecto

### 4.1 Instalar dependencias

```bash
pip install -r requirements.txt
```

Contenido actual de `requirements.txt`:

```text
pandas
openpyxl
plotly
numpy
```

### 4.2 Generar el dashboard HTML principal

```bash
python app.py
```

Esto:

- Lee `modelo_estrella_ventas.xlsx`.
- Crea la carpeta `graficos/` si no existe.
- Genera 8 gráficos HTML individuales.
- Genera `graficos/index.html` como landing page con KPIs y enlaces a cada gráfico.

### 4.3 Generar el informe ejecutivo

```bash
python generar_informe.py
```

Esto produce `graficos/informe_modelo_estrella.html`, un informe más formal con KPIs, hallazgos y visuales incrustados.

### 4.4 Generar visuales para el archivo PBIP

```bash
python generar_visuales_pbip.py
```

Esto:

- Reemplaza el contenido de `modeloEstrella.Report/definition/pages/1d59b4583cfd82f8dfde/visuals/`.
- Actualiza `page.json` con dimensiones y nombre de página.
- Requiere que el modelo semántico ya exista con las tablas referenciadas.

### 4.5 Abrir los resultados

- Navegador: abrir `graficos/index.html` o `graficos/informe_modelo_estrella.html`.
- Power BI Desktop: abrir `modeloEstrella.pbip` o `modeloEstrella.pbix`.

---

## 5. Arquitectura del código

### 5.1 `app.py`

Script procedural con tres responsabilidades principales:

1. `load_data()` — carga las 5 hojas del Excel y ajusta tipos de datos.
2. `merge_data(...)` — realiza left joins entre `Fact_Ventas` y las 4 dimensiones.
3. `create_dashboard()` — agrupa los datos, genera 8 figuras Plotly y escribe `graficos/index.html`.

### 5.2 `generar_informe.py`

Versión más elaborada del reporte:

- Usa `pathlib.Path` para rutas relativas al script.
- Define helpers de formato: `money()`, `number()`, `pct()`.
- Aplica un estilo corporativo unificado con `style_figure()`.
- Genera un solo HTML con múltiples paneles, KPIs e insights automáticos.

### 5.3 `generar_visuales_pbip.py`

Genera definiciones de visuales de Power BI en formato JSON:

- Helpers para expresiones DAX, agregaciones y proyecciones.
- Crea carpetas bajo `modeloEstrella.Report/definition/pages/.../visuals/`.
- Actualiza `page.json`.

---

## 6. Convenciones de desarrollo

- **Idioma:** el código, comentarios, README y documentación están en **español**. Se recomienda mantener ese idioma para coherencia.
- **Estilo:** scripts procedurales, sin clases ni framework. Cada script es autocontenido y ejecutable directamente (`if __name__ == "__main__":`).
- **Rutas:** se usan rutas relativas al directorio de trabajo (`"modelo_estrella_ventas.xlsx"`) o relativas al script (`Path(__file__).resolve().parent`).
- **Nombres de archivos de salida:** los gráficos individuales usan prefijo numérico (`01_`, `02_`, etc.).
- **Colores:** cada gráfico usa una escala continua o paleta cualitativa diferente (Blues, Greens, Reds, Purples, Set3, etc.).

---

## 7. Pruebas

**No hay pruebas automatizadas en este proyecto.** No existen archivos `test_*.py`, `pytest.ini`, ni configuración de linting.

Para validar cambios, la estrategia actual es:

1. Ejecutar el script correspondiente.
2. Verificar que los archivos HTML se generen sin errores.
3. Abrir `graficos/index.html` en un navegador y comprobar los gráficos.
4. Si se modifica el PBIP, abrir `modeloEstrella.pbip` en Power BI Desktop y validar que los visuales carguen.

Si se añaden tests, se recomienda usar `pytest` y ubicarlos en un directorio `tests/`.

---

## 8. Consideraciones de seguridad

- No hay secretos, credenciales ni variables de entorno en el repositorio.
- El archivo Excel contiene datos de ejemplo/sintéticos de ventas. Verificar antes de publicar si contiene información real.
- Los archivos HTML de salida son estáticos y no ejecutan código del servidor, pero incluyen JavaScript de Plotly vía CDN (en `generar_informe.py`). Si se comparten offline, considerar embeber `plotly.js` localmente.
- El modelo de Power BI referencia una ruta absoluta de Windows (`G:\My Drive\...\modelo_estrella_ventas.xlsx`) en las expresiones M de las particiones. Mover el proyecto a otra ubicación puede romper la recarga de datos en Power BI Desktop.

---

## 9. Despliegue

No hay un proceso de despliegue automatizado. Las opciones actuales son:

- **HTML:** compartir la carpeta `graficos/` o publicar los archivos HTML en cualquier servidor web estático.
- **Power BI:** abrir `modeloEstrella.pbix` en Power BI Desktop y publicar al servicio de Power BI.

---

## 10. Notas para mantenedores

- Si se actualiza `modelo_estrella_ventas.xlsx`, volver a ejecutar `python app.py` y, si aplica, `python generar_informe.py`.
- Si se cambian columnas del Excel, también hay que actualizar:
  - Las hojas/columnas leídas en `app.py` y `generar_informe.py`.
  - Las definiciones de tablas en `modeloEstrella.SemanticModel/definition/tables/*.tmdl`.
  - Las referencias en `generar_visuales_pbip.py`.
- Los archivos bajo `.pbi/` y `cache.abf` están ignorados por `.gitignore` y no deben versionarse.
