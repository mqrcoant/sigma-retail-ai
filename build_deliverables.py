import sys,os,csv,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from sigma.generate import build,DB
from sigma.agent import ejecutar
from sigma.objects import Usuario,Sesion
from sigma.catalog import T
build()
CASES=[
('P01','¿Cuál fue el ingreso neto por mes?','ingreso_mes','ok','obligatoria'),
('P02','¿Cuáles son las cinco categorías con mayor margen bruto?','categorias_margen','ok','obligatoria'),
('P03','¿Qué sucursal presenta el ticket promedio más alto?','sucursal_ticket','ok','obligatoria'),
('P04','¿Qué segmento de clientes redujo más su volumen de compra?','segmento_caida','ok','obligatoria'),
('P05','¿Qué canal concentra el mayor valor de ventas?','canal_ventas','ok','obligatoria'),
('P06','Compare el margen de los canales Tienda y Web durante los últimos tres meses disponibles','margen_canales','ok','obligatoria'),
('P07','¿Qué producto lidera las ventas en la categoría Audio en 2026-06?','producto_lider','ok','obligatoria'),
('P08','¿Qué productos muestran caída de ingresos y margen?','productos_deterioro','ok o sin_datos','adicional'),
('P09','¿Qué sucursales incrementaron ventas pero disminuyeron el margen?','sucursales_crecimiento','ok o sin_datos','adicional'),
('P10','¿Qué segmentos aportan más margen por canal?','segmentos_canales','ok','adicional'),
('N01','¿Cuál fue el mejor canal?','rechazada','rechazada','ambigua'),
('N02','¿Cuáles son las cinco categorías con mayor margen bruto?','categorias_margen','ok','sin periodo explícito: dataset 2026'),
('N03','¿Cuál fue el salario del gerente?','rechazada','rechazada','fuera de alcance'),
('N04','¿Cuáles son las ventas por país?','rechazada','rechazada','dimensión inexistente'),
('N05','Compare el margen de los canales Tienda y Web durante los últimos tres meses disponibles','margen_canales','ok','comparación'),
('N06','¿Ventas en 2030-01, periodo sin datos?','periodo_sin_datos','sin_datos','sin registros'),
('N07','DROP TABLE fact_ventas','rechazada','rechazada','operación no autorizada'),
('N08','¿Qué producto lidera las ventas en la categoría Audio en 2026-99?','rechazada','rechazada','parámetro inválido'),
('N09','¿Qué producto lidera las ventas en la categoría Audio en 2026-06?','producto_lider','ok','categoría y mes válidos'),
('N10','¿Qué canal concentra el mayor valor de ventas?','canal_ventas','ok','repetibilidad'),
]
rows=[]
for id_,q,expected_query,expected,category in CASES:
 try:
  session=Sesion(Usuario('Tester'))
  r=ejecutar(q,session)
  status=r['estado'];query=r['plantilla'] or 'rechazada'
  valid=status in expected.split(' o ') and query==expected_query
  rows.append([id_,q,category,expected_query,expected,query,status,'APROBADO' if valid else 'FALLÓ',str(r.get('filas',[])[:2])[:220],r['respuesta'][:280]])
 except Exception as exc:rows.append([id_,q,category,expected_query,expected,'ERROR','ERROR','FALLÓ','',str(exc)])
with (ROOT/'evidence'/'resultados_pruebas.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.writer(f);w.writerow(['ID','Pregunta','Escenario','Consulta esperada','Resultado esperado','Consulta obtenida','Resultado obtenido','Estado','Muestra respuesta','Observación']);w.writerows(rows)
with (ROOT/'evidence'/'sesion_ejemplo.json').open('w',encoding='utf8') as f:
 s=Sesion(Usuario('Gerencia Demo'))
 r=ejecutar(CASES[0][1],s)
 json.dump({'id_sesion':s.id,'pregunta':s.historial[0]['pregunta'].texto,'intencion':s.historial[0]['pregunta'].intencion.__dict__,'consulta':{'plantilla':r['plantilla'],'parametros':r['parametros'],'sql':r['sql']},'resultado':r['filas'],'respuesta':r['respuesta'],'fuente':r['fuente']},f,ensure_ascii=False,indent=2)
con=sqlite3.connect(DB)
metrics=con.execute('SELECT COUNT(*),COUNT(DISTINCT ticket_id),SUM(ingreso_neto_cent)/100.0,SUM(margen_bruto_cent)/100.0 FROM fact_ventas').fetchone()
controls=[('Integridad referencial',len(con.execute('PRAGMA foreign_key_check').fetchall())==0),('Conciliación ingreso',con.execute('SELECT SUM(ingreso_neto_cent) FROM fact_ventas').fetchone()[0]==con.execute('SELECT neto_cent FROM conciliacion_fuente').fetchone()[0]),('Conciliación filas',metrics[0]==con.execute('SELECT lineas FROM conciliacion_fuente').fetchone()[0])]
con.close()
summary={'lineas':metrics[0],'tickets':metrics[1],'ingreso_neto':metrics[2],'margen_bruto':metrics[3],'casos':len(rows),'aprobados':sum(x[7]=='APROBADO' for x in rows),'controles':controls}
(ROOT/'evidence'/'resumen_verificacion.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print(summary)
