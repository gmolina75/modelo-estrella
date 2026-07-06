import json
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PAGE_DIR = BASE_DIR / "modeloEstrella.Report" / "definition" / "pages" / "1d59b4583cfd82f8dfde"
VISUALS_DIR = PAGE_DIR / "visuals"
VISUAL_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json"


def source(table):
    return {"SourceRef": {"Entity": table}}


def column(table, prop):
    return {"Column": {"Expression": source(table), "Property": prop}}


def aggregate_sum(table, prop):
    return {"Aggregation": {"Expression": column(table, prop), "Function": 0}}


def aggregate_distinct(table, prop):
    return {"Aggregation": {"Expression": column(table, prop), "Function": 2}}


def projection(field, query_ref, display_name=None, fmt=None):
    item = {
        "field": field,
        "queryRef": query_ref,
        "nativeQueryRef": query_ref,
    }
    if display_name:
        item["displayName"] = display_name
    if fmt:
        item["format"] = fmt
    return item


def role(*items):
    return {"projections": list(items)}


def container_objects(title, background="#FFFFFF"):
    return {
        "title": [
            {
                "properties": {
                    "show": True,
                    "text": title,
                    "fontSize": 12,
                    "bold": True,
                    "fontColor": {"solid": {"color": "#1D2730"}},
                }
            }
        ],
        "background": [
            {
                "properties": {
                    "show": True,
                    "color": {"solid": {"color": background}},
                    "transparency": 0,
                }
            }
        ],
        "border": [
            {
                "properties": {
                    "show": True,
                    "color": {"solid": {"color": "#DCE3EA"}},
                    "radius": 6,
                    "width": 1,
                }
            }
        ],
        "padding": [
            {
                "properties": {
                    "top": 8,
                    "bottom": 8,
                    "left": 8,
                    "right": 8,
                }
            }
        ],
    }


def visual(name, visual_type, x, y, width, height, z, query_state, title, sort_field=None):
    config = {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "width": width,
            "height": height,
            "tabOrder": z,
        },
        "visual": {
            "visualType": visual_type,
            "query": {
                "queryState": query_state,
            },
            "visualContainerObjects": container_objects(title),
        },
        "howCreated": "Default",
    }
    if sort_field is not None:
        config["visual"]["query"]["sortDefinition"] = {
            "sort": [{"field": sort_field, "direction": "Descending"}],
            "isDefaultSort": False,
        }
    return config


def write_visual(config):
    folder = VISUALS_DIR / config["name"]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "visual.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def update_page():
    page_path = PAGE_DIR / "page.json"
    page = json.loads(page_path.read_text(encoding="utf-8"))
    page["displayName"] = "Informe Ventas"
    page["displayOption"] = "FitToPage"
    page["height"] = 720
    page["width"] = 1280
    page_path.write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build():
    if VISUALS_DIR.exists():
        shutil.rmtree(VISUALS_DIR)
    VISUALS_DIR.mkdir(parents=True, exist_ok=True)

    ventas = aggregate_sum("Fact_Ventas", "Monto_Neto")
    bruto = aggregate_sum("Fact_Ventas", "Monto_Bruto")
    descuento = aggregate_sum("Fact_Ventas", "Descuento")
    cantidad = aggregate_sum("Fact_Ventas", "Cantidad")
    transacciones = aggregate_distinct("Fact_Ventas", "ID_Venta")
    clientes = aggregate_distinct("Fact_Ventas", "ID_Cliente")

    categoria = column("Dim_Producto", "Categoría")
    producto = column("Dim_Producto", "Nombre_Producto")
    pais = column("Dim_Cliente", "País")
    segmento = column("Dim_Cliente", "Segmento")
    region = column("Dim_Vendedor", "Región")
    fecha = column("Dim_Tiempo", "Fecha")
    trimestre = column("Dim_Tiempo", "Trimestre")

    money_fmt = "$#,0.00;($#,0.00);$0.00"
    int_fmt = "#,0"

    visuals = [
        visual(
            "kpi_total_ventas",
            "card",
            20,
            20,
            295,
            92,
            1,
            {"Values": role(projection(ventas, "Sum(Fact_Ventas.Monto_Neto)", "Total ventas", money_fmt))},
            "Total ventas netas",
        ),
        visual(
            "kpi_transacciones",
            "card",
            330,
            20,
            295,
            92,
            2,
            {"Values": role(projection(transacciones, "DistinctCount(Fact_Ventas.ID_Venta)", "Transacciones", int_fmt))},
            "Transacciones",
        ),
        visual(
            "kpi_clientes",
            "card",
            640,
            20,
            295,
            92,
            3,
            {"Values": role(projection(clientes, "DistinctCount(Fact_Ventas.ID_Cliente)", "Clientes", int_fmt))},
            "Clientes únicos",
        ),
        visual(
            "kpi_descuentos",
            "card",
            950,
            20,
            310,
            92,
            4,
            {"Values": role(projection(descuento, "Sum(Fact_Ventas.Descuento)", "Descuentos", money_fmt))},
            "Total descuentos",
        ),
        visual(
            "ventas_categoria",
            "clusteredColumnChart",
            20,
            130,
            400,
            245,
            5,
            {
                "Category": role(projection(categoria, "Dim_Producto.Categoría", "Categoría")),
                "Y": role(projection(ventas, "Sum(Fact_Ventas.Monto_Neto)", "Ventas", money_fmt)),
            },
            "Ventas por categoría",
            ventas,
        ),
        visual(
            "ventas_tiempo",
            "lineChart",
            440,
            130,
            400,
            245,
            6,
            {
                "Category": role(projection(fecha, "Dim_Tiempo.Fecha", "Fecha")),
                "Y": role(projection(ventas, "Sum(Fact_Ventas.Monto_Neto)", "Ventas", money_fmt)),
            },
            "Evolución de ventas en el tiempo",
        ),
        visual(
            "ventas_region",
            "donutChart",
            860,
            130,
            400,
            245,
            7,
            {
                "Category": role(projection(region, "Dim_Vendedor.Región", "Región")),
                "Y": role(projection(ventas, "Sum(Fact_Ventas.Monto_Neto)", "Ventas", money_fmt)),
            },
            "Participación por región",
            ventas,
        ),
        visual(
            "top_paises",
            "barChart",
            20,
            395,
            400,
            305,
            8,
            {
                "Category": role(projection(pais, "Dim_Cliente.País", "País")),
                "Y": role(projection(ventas, "Sum(Fact_Ventas.Monto_Neto)", "Ventas", money_fmt)),
            },
            "Ventas por país",
            ventas,
        ),
        visual(
            "top_productos",
            "barChart",
            440,
            395,
            400,
            305,
            9,
            {
                "Category": role(projection(producto, "Dim_Producto.Nombre_Producto", "Producto")),
                "Y": role(projection(ventas, "Sum(Fact_Ventas.Monto_Neto)", "Ventas", money_fmt)),
            },
            "Ventas por producto",
            ventas,
        ),
        visual(
            "descuentos_vs_ventas",
            "scatterChart",
            860,
            395,
            400,
            305,
            10,
            {
                "X": role(projection(descuento, "Sum(Fact_Ventas.Descuento)", "Descuento", money_fmt)),
                "Y": role(projection(ventas, "Sum(Fact_Ventas.Monto_Neto)", "Ventas", money_fmt)),
                "Size": role(projection(cantidad, "Sum(Fact_Ventas.Cantidad)", "Cantidad", int_fmt)),
                "Details": role(projection(producto, "Dim_Producto.Nombre_Producto", "Producto")),
            },
            "Descuentos vs ventas netas",
        ),
    ]

    for item in visuals:
        write_visual(item)

    update_page()
    return len(visuals)


if __name__ == "__main__":
    print(f"Visuales generados: {build()}")
