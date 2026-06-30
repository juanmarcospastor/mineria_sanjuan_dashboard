# Monitor Interactivo de Minería de San Juan

Demo completo en **Flask + Plotly + SQLite/PostgreSQL** para construir un tablero minero provincial con exportaciones, precios internacionales, destinos, composición por producto, balance comercial y volumen físico implícito.

## 1. Qué incluye

- Aplicación Flask.
- Gráficos interactivos con Plotly.
- Base de datos SQLite lista para usar.
- Compatibilidad con PostgreSQL cambiando `DATABASE_URL`.
- Script de carga demo.
- Script importador de CSV.
- Estructura de datos documentada.
- Vista de tablero y vista de revisión de datos.

## 2. Estructura del proyecto

```text
mineria_sanjuan_dashboard/
├─ app/
│  ├─ __init__.py
│  ├─ models.py
│  ├─ routes.py
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ dashboard.html
│  │  └─ datos.html
│  └─ static/
│     ├─ css/styles.css
│     └─ js/dashboard.js
├─ data/
├─ docs/
│  └─ estructura_datos.md
├─ scripts/
│  ├─ seed_demo.py
│  └─ import_csv.py
├─ .env.example
├─ requirements.txt
└─ run.py
```

## 3. Instalación en Windows

Abrí una terminal en la carpeta donde descomprimas el proyecto y ejecutá:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts\seed_demo.py
python run.py
```

Después abrí:

```text
http://127.0.0.1:5000
```

## 4. Instalación en Linux/Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_demo.py
python run.py
```

## 5. Usar PostgreSQL

Crear base:

```sql
CREATE DATABASE mineria_sanjuan;
```

Editar `.env`:

```text
DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/mineria_sanjuan
```

Luego ejecutar:

```bash
python scripts/seed_demo.py
python run.py
```

## 6. Reemplazar datos demo por datos reales

Prepará CSV con las columnas indicadas en `docs/estructura_datos.md` y ejecutá, por ejemplo:

```bash
python scripts/import_csv.py data/exportaciones_provinciales.csv exportaciones_provinciales
python scripts/import_csv.py data/exportaciones_productos.csv exportaciones_productos
python scripts/import_csv.py data/exportaciones_destinos.csv exportaciones_destinos
python scripts/import_csv.py data/precios_minerales.csv precios_minerales
python scripts/import_csv.py data/balances_comerciales.csv balances_comerciales
```

## 7. Próximas mejoras recomendadas

- Agregar login si el tablero se usa para clientes.
- Agregar carga desde Excel con varias hojas.
- Agregar módulo de escenarios de cobre para Los Azules y Vicuña.
- Agregar mapa de proyectos con coordenadas.
- Agregar generación automática de resumen ejecutivo mensual.
- Agregar comparación contra PBG, empleo, regalías y recaudación provincial.
