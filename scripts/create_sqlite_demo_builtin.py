"""Crea una base SQLite demo sin dependencias externas. Ya se ejecutó para dejar instance/mineria_sanjuan.db lista."""
from pathlib import Path
import sqlite3, math, random
ROOT = Path(__file__).resolve().parents[1]
DBDIR = ROOT / "instance"
DBDIR.mkdir(exist_ok=True)
DBPATH = DBDIR / "mineria_sanjuan.db"
random.seed(7)
con = sqlite3.connect(DBPATH)
cur = con.cursor()
for t in ["exportaciones_provinciales","exportaciones_productos","exportaciones_destinos","precios_minerales","balances_comerciales"]:
    cur.execute(f"DROP TABLE IF EXISTS {t}")
cur.execute('''CREATE TABLE exportaciones_provinciales (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, provincia TEXT NOT NULL, exportaciones_mineras_usd REAL NOT NULL, exportaciones_totales_usd REAL, variacion_interanual_pct REAL, fuente TEXT)''')
cur.execute('''CREATE TABLE exportaciones_productos (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, provincia TEXT NOT NULL, producto TEXT NOT NULL, valor_fob_usd REAL NOT NULL, participacion_pct REAL, fuente TEXT)''')
cur.execute('''CREATE TABLE exportaciones_destinos (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, provincia TEXT NOT NULL, destino TEXT NOT NULL, valor_fob_usd REAL NOT NULL, participacion_pct REAL, fuente TEXT)''')
cur.execute('''CREATE TABLE precios_minerales (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, mineral TEXT NOT NULL, precio_usd REAL NOT NULL, unidad TEXT NOT NULL, variacion_interanual_pct REAL, variacion_mensual_pct REAL, fuente TEXT)''')
cur.execute('''CREATE TABLE balances_comerciales (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, alcance TEXT NOT NULL, exportaciones_usd REAL NOT NULL, importaciones_usd REAL NOT NULL, balance_usd REAL NOT NULL, fuente TEXT)''')
PROVINCIAS=["San Juan","Santa Cruz","Jujuy","Salta","Catamarca"]
MESES=[]
for y in [2024,2025,2026]:
    for m in range(1,13 if y<2026 else 5): MESES.append(f"{y}-{m:02d}")
base={"San Juan":150e6,"Santa Cruz":210e6,"Jujuy":95e6,"Salta":55e6,"Catamarca":40e6}
grow={"San Juan":.018,"Santa Cruz":.025,"Jujuy":.020,"Salta":.023,"Catamarca":.030}
over={"San Juan":(233e6,77.9),"Santa Cruz":(286e6,73.8),"Jujuy":(145e6,65.0),"Salta":(87e6,92.0),"Catamarca":(53e6,80.0)}
prod={"San Juan":[("Oro",.981),("Cales",.014),("Otros",.005)],"Santa Cruz":[("Oro",.851),("Plata",.148),("Otros",.001)],"Jujuy":[("Litio",.94),("Otros",.06)],"Salta":[("Litio",.96),("Otros",.04)],"Catamarca":[("Litio",.88),("Oro",.10),("Otros",.02)]}
dest={"San Juan":[("Suiza",.641),("India",.316),("Canadá",.024),("Resto",.019)],"Santa Cruz":[("Suiza",.401),("Estados Unidos",.285),("Canadá",.166),("Resto",.148)],"Jujuy":[("China",.52),("Corea del Sur",.21),("Japón",.14),("Resto",.13)],"Salta":[("China",.49),("Estados Unidos",.18),("Japón",.14),("Resto",.19)],"Catamarca":[("China",.46),("Japón",.20),("Corea del Sur",.18),("Resto",.16)]}
inc={"San Juan":.91,"Santa Cruz":.883,"Jujuy":.872,"Salta":.614,"Catamarca":.959}
valores={}
fuente="Demo basado en informes DNPEM"
for i,fecha in enumerate(MESES):
    total=0
    for p in PROVINCIAS:
        v=base[p]*((1+grow[p])**i)*(1+.18*math.sin(i/2.7))*random.uniform(.88,1.14)
        var=None
        if i>=12:
            var=(v/valores[(MESES[i-12],p)]-1)*100
        if fecha=="2026-04": v,var=over[p]
        valores[(fecha,p)]=v; total+=v
        cur.execute("INSERT INTO exportaciones_provinciales(fecha,provincia,exportaciones_mineras_usd,exportaciones_totales_usd,variacion_interanual_pct,fuente) VALUES(?,?,?,?,?,?)",(fecha,p,v,v/inc[p],var,fuente))
        for pr,sh in prod[p]: cur.execute("INSERT INTO exportaciones_productos(fecha,provincia,producto,valor_fob_usd,participacion_pct,fuente) VALUES(?,?,?,?,?,?)",(fecha,p,pr,v*sh,sh*100,fuente))
        for d,sh in dest[p]: cur.execute("INSERT INTO exportaciones_destinos(fecha,provincia,destino,valor_fob_usd,participacion_pct,fuente) VALUES(?,?,?,?,?,?)",(fecha,p,d,v*sh,sh*100,fuente))
    cur.execute("INSERT INTO exportaciones_provinciales(fecha,provincia,exportaciones_mineras_usd,exportaciones_totales_usd,variacion_interanual_pct,fuente) VALUES(?,?,?,?,?,?)",(fecha,"Argentina",total,None,None,fuente))
    imp=total*random.uniform(.12,.20); cur.execute("INSERT INTO balances_comerciales(fecha,alcance,exportaciones_usd,importaciones_usd,balance_usd,fuente) VALUES(?,?,?,?,?,?)",(fecha,"Minerales Argentina",total,imp,total-imp,fuente))
    imp2=total*random.uniform(.05,.10); cur.execute("INSERT INTO balances_comerciales(fecha,alcance,exportaciones_usd,importaciones_usd,balance_usd,fuente) VALUES(?,?,?,?,?,?)",(fecha,"Principales proyectos",total*.965,imp2,total*.965-imp2,fuente))
precios={"Oro":("USD/Ozt",1800,4721),"Plata":("USD/Ozt",22.5,75.9),"Cobre":("USD/tn",9200,12951),"Carbonato de litio":("USD/tn",11500,21263)}
n=len(MESES)
for mineral,(unidad,ini,fin) in precios.items():
    for i,fecha in enumerate(MESES):
        t=i/(n-1); precio=(ini*(1-t)+fin*t)*(1+.08*math.sin(i/3.1))
        if fecha=="2026-04": precio=fin
        cur.execute("INSERT INTO precios_minerales(fecha,mineral,precio_usd,unidad,variacion_interanual_pct,variacion_mensual_pct,fuente) VALUES(?,?,?,?,?,?,?)",(fecha,mineral,precio,unidad,None,None,fuente))
con.commit(); con.close(); print(DBPATH)
