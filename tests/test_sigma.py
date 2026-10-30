from sigma.generate import build,DB
from sigma.agent import ejecutar,interpretar
from sigma.objects import Sesion,Usuario
import sqlite3

def setup_module():build()
questions=['¿Cuál fue el ingreso neto por mes?','¿Cuáles son las cinco categorías con mayor margen bruto?','¿Qué sucursal presenta el ticket promedio más alto?','¿Qué segmento de clientes redujo más su volumen de compra?','¿Qué canal concentra el mayor valor de ventas?','Compare el margen de los canales Tienda y Web durante los últimos tres meses disponibles','¿Qué producto lidera las ventas en la categoría Audio en 2026-06?','¿Qué productos muestran caída de ingresos y margen?','¿Qué sucursales incrementaron ventas pero disminuyeron el margen?','¿Qué segmentos aportan más margen por canal?']
def test_all_required_queries():
 for q in questions:
  r=ejecutar(q,Sesion(Usuario('QA')))
  assert r['estado'] in ('ok','sin_datos'),(q,r)
def test_negative_cases():
 for q in ['¿Cuál fue el mejor canal?','¿Cuál fue el salario del gerente?','¿Ventas por país?','DROP TABLE fact_ventas','¿Ventas en 2030-01, periodo sin datos?']:
  r=ejecutar(q,Sesion(Usuario('QA')))
  assert r['estado'] in ('rechazada','sin_datos')
def test_reconciliation():
 c=sqlite3.connect(DB);a=c.execute('SELECT SUM(ingreso_neto_cent),SUM(margen_bruto_cent),COUNT(*) FROM fact_ventas').fetchone();b=c.execute('SELECT neto_cent,neto_cent-costo_cent,lineas FROM conciliacion_fuente').fetchone();assert a==b
 assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
 assert c.execute('SELECT COUNT(*) FROM fact_ventas f JOIN dim_cliente cl ON f.cliente_sk=cl.cliente_sk JOIN dim_tiempo t ON f.tiempo_sk=t.tiempo_sk WHERE t.fecha NOT BETWEEN cl.vigente_desde AND cl.vigente_hasta').fetchone()[0]==0
 c.close()
def test_ticket_unique():
 c=sqlite3.connect(DB);rows,tickets=c.execute('SELECT COUNT(*),COUNT(DISTINCT ticket_id) FROM fact_ventas').fetchone();assert rows>tickets;c.close()

def test_polimorfismo_reglas():
 from sigma.objects import ReglaSoloLectura,ReglaFilasNoNegativas
 reglas=[ReglaSoloLectura('solo lectura',True,''),ReglaFilasNoNegativas('filas',True,'')]
 assert reglas[0].verificar({'sql':'SELECT 1'})
 assert not reglas[0].verificar({'sql':'DELETE FROM fact_ventas'})
 assert reglas[1].verificar({'num_filas':0})
 assert not reglas[1].verificar({'num_filas':-1})
