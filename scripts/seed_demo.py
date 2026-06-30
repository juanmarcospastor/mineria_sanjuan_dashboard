"""
Carga datos ficticios/demostrativos para probar el tablero.
Ejecutar desde la carpeta raíz del proyecto:

    python scripts/seed_demo.py

Los valores son de demo y algunos puntos de referencia replican magnitudes mencionadas en informes 2026.
Reemplazar por las bases reales de la Dirección Nacional de Promoción y Economía Minera.
"""
from pathlib import Path
import sys
import math
import random

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app import create_app, db  # noqa: E402
from app.models import ExportacionProvincial, ExportacionProducto, ExportacionDestino, PrecioMineral, BalanceComercial  # noqa: E402

random.seed(7)

app = create_app()

PROVINCIAS = ["San Juan", "Santa Cruz", "Jujuy", "Salta", "Catamarca"]
MESES = []
for y in [2024, 2025, 2026]:
    max_m = 12 if y < 2026 else 4
    for m in range(1, max_m + 1):
        MESES.append(f"{y}-{m:02d}")

base_prov = {
    "San Juan": 150_000_000,
    "Santa Cruz": 210_000_000,
    "Jujuy": 95_000_000,
    "Salta": 55_000_000,
    "Catamarca": 40_000_000,
}
crecimiento = {
    "San Juan": 0.018,
    "Santa Cruz": 0.025,
    "Jujuy": 0.020,
    "Salta": 0.023,
    "Catamarca": 0.030,
}

# Sobrescribimos abril 2026 para acercar magnitudes del informe mensual.
ovverrides_202604 = {
    "San Juan": (233_000_000, 77.9),
    "Santa Cruz": (286_000_000, 73.8),
    "Jujuy": (145_000_000, 65.0),
    "Salta": (87_000_000, 92.0),
    "Catamarca": (53_000_000, 80.0),
}

precios = {
    "Oro": {"unidad": "USD/Ozt", "inicio": 1800, "fin": 4721},
    "Plata": {"unidad": "USD/Ozt", "inicio": 22.5, "fin": 75.9},
    "Cobre": {"unidad": "USD/tn", "inicio": 9200, "fin": 12951},
    "Carbonato de litio": {"unidad": "USD/tn", "inicio": 11500, "fin": 21263},
}

productos_por_prov = {
    "San Juan": [("Oro", 0.981), ("Cales", 0.014), ("Otros", 0.005)],
    "Santa Cruz": [("Oro", 0.851), ("Plata", 0.148), ("Otros", 0.001)],
    "Jujuy": [("Litio", 0.94), ("Otros", 0.06)],
    "Salta": [("Litio", 0.96), ("Otros", 0.04)],
    "Catamarca": [("Litio", 0.88), ("Oro", 0.10), ("Otros", 0.02)],
}

destinos_por_prov = {
    "San Juan": [("Suiza", 0.641), ("India", 0.316), ("Canadá", 0.024), ("Resto", 0.019)],
    "Santa Cruz": [("Suiza", 0.401), ("Estados Unidos", 0.285), ("Canadá", 0.166), ("Resto", 0.148)],
    "Jujuy": [("China", 0.52), ("Corea del Sur", 0.21), ("Japón", 0.14), ("Resto", 0.13)],
    "Salta": [("China", 0.49), ("Estados Unidos", 0.18), ("Japón", 0.14), ("Resto", 0.19)],
    "Catamarca": [("China", 0.46), ("Japón", 0.20), ("Corea del Sur", 0.18), ("Resto", 0.16)],
}


def fuente(nombre):
    return f"Demo basado en estructura de informes DNPEM - {nombre}"


with app.app_context():
    db.drop_all()
    db.create_all()

    valores_mes = {}
    for i, fecha in enumerate(MESES):
        total_arg = 0
        for prov in PROVINCIAS:
            estacional = 1 + 0.18 * math.sin(i / 2.7)
            ruido = random.uniform(0.88, 1.14)
            valor = base_prov[prov] * ((1 + crecimiento[prov]) ** i) * estacional * ruido
            var_ia = None
            if i >= 12:
                prev = valores_mes.get((MESES[i-12], prov), valor)
                var_ia = (valor / prev - 1) * 100
            if fecha == "2026-04":
                valor, var_ia = ovverrides_202604[prov]
            valores_mes[(fecha, prov)] = valor
            total_arg += valor

            # Para total provincial estimamos un denominador que permite medir incidencia minera.
            incidencia = {
                "San Juan": 0.91,
                "Santa Cruz": 0.883,
                "Jujuy": 0.872,
                "Salta": 0.614,
                "Catamarca": 0.959,
            }[prov]
            total_exportado_prov = valor / incidencia
            db.session.add(ExportacionProvincial(
                fecha=fecha,
                provincia=prov,
                exportaciones_mineras_usd=round(valor, 2),
                exportaciones_totales_usd=round(total_exportado_prov, 2),
                variacion_interanual_pct=round(var_ia, 1) if var_ia is not None else None,
                fuente=fuente("Origen Provincial"),
            ))

            for prod, share in productos_por_prov[prov]:
                db.session.add(ExportacionProducto(
                    fecha=fecha, provincia=prov, producto=prod,
                    valor_fob_usd=round(valor * share, 2), participacion_pct=share * 100,
                    fuente=fuente("Producto"),
                ))
            for dest, share in destinos_por_prov[prov]:
                db.session.add(ExportacionDestino(
                    fecha=fecha, provincia=prov, destino=dest,
                    valor_fob_usd=round(valor * share, 2), participacion_pct=share * 100,
                    fuente=fuente("Destino"),
                ))

        db.session.add(ExportacionProvincial(
            fecha=fecha,
            provincia="Argentina",
            exportaciones_mineras_usd=round(total_arg, 2),
            exportaciones_totales_usd=None,
            variacion_interanual_pct=None,
            fuente=fuente("Exportaciones Mineras Argentina"),
        ))

        # Balance comercial demo
        imp_minerales = total_arg * random.uniform(0.12, 0.20)
        db.session.add(BalanceComercial(
            fecha=fecha,
            alcance="Minerales Argentina",
            exportaciones_usd=round(total_arg, 2),
            importaciones_usd=round(imp_minerales, 2),
            balance_usd=round(total_arg - imp_minerales, 2),
            fuente=fuente("Balance Comercial de Minerales"),
        ))
        imp_proyectos = total_arg * random.uniform(0.05, 0.10)
        db.session.add(BalanceComercial(
            fecha=fecha,
            alcance="Principales proyectos",
            exportaciones_usd=round(total_arg * 0.965, 2),
            importaciones_usd=round(imp_proyectos, 2),
            balance_usd=round(total_arg * 0.965 - imp_proyectos, 2),
            fuente=fuente("Balance Comercial de Proyectos"),
        ))

    # Precios minerales: crecimiento suavizado hasta abril 2026.
    n = len(MESES)
    for mineral, cfg in precios.items():
        for i, fecha in enumerate(MESES):
            t = i / (n - 1)
            precio = cfg["inicio"] * (1 - t) + cfg["fin"] * t
            precio *= 1 + 0.08 * math.sin(i / 3.1)
            if fecha == "2026-04":
                precio = cfg["fin"]
            precio_prev = cfg["inicio"] if i == 0 else None
            db.session.add(PrecioMineral(
                fecha=fecha,
                mineral=mineral,
                precio_usd=round(precio, 2),
                unidad=cfg["unidad"],
                variacion_interanual_pct=None,
                variacion_mensual_pct=None,
                fuente=fuente("Precios principales minerales"),
            ))

    db.session.commit()
    print("Base demo cargada correctamente.")
