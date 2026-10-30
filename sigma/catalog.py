"""Catálogo de preguntas y SQL parametrizado. Importes almacenados en céntimos."""
from dataclasses import dataclass
@dataclass(frozen=True)
class Template:
 code:str
 sql:str
 metric:str
 dimension:str
 rule:str
 parameters:tuple=()
BASE=' FROM fact_ventas f JOIN dim_tiempo t ON t.tiempo_sk=f.tiempo_sk JOIN dim_producto p ON p.producto_sk=f.producto_sk JOIN dim_cliente cl ON cl.cliente_sk=f.cliente_sk JOIN dim_sucursal s ON s.sucursal_sk=f.sucursal_sk JOIN dim_canal ca ON ca.canal_sk=f.canal_sk '
T={}
def add(code,sql,metric,dimension,rule,parameters=()):T[code]=Template(code,sql,metric,dimension,rule,parameters)
add('ingreso_mes','SELECT t.anio_mes etiqueta, ROUND(SUM(f.ingreso_neto_cent)/100.0,2) valor'+BASE+'GROUP BY t.anio_mes ORDER BY t.anio_mes','Ingreso neto','mes','SUM(bruto-descuento-devolución)')
add('categorias_margen','SELECT p.categoria etiqueta,ROUND(SUM(f.margen_bruto_cent)/100.0,2) valor'+BASE+'GROUP BY p.categoria ORDER BY valor DESC LIMIT 5','Margen bruto','categoría','SUM(ingreso neto-costo)')
add('sucursal_ticket','SELECT s.nombre etiqueta,ROUND(SUM(f.ingreso_neto_cent)*1.0/COUNT(DISTINCT f.ticket_id)/100.0,2) valor'+BASE+'GROUP BY s.sucursal_sk ORDER BY valor DESC LIMIT 1','Ticket promedio','sucursal','SUM(neto)/COUNT(DISTINCT ticket_id)')
add('segmento_caida',"SELECT cl.segmento etiqueta, ROUND(SUM(CASE WHEN t.mes BETWEEN 7 AND 12 THEN f.cantidad ELSE 0 END)-SUM(CASE WHEN t.mes BETWEEN 1 AND 6 THEN f.cantidad ELSE 0 END),2) valor"+BASE+'GROUP BY cl.segmento ORDER BY valor ASC LIMIT 1','Variación de unidades','segmento histórico','Unidades segundo semestre - primero')
add('canal_ventas','SELECT ca.nombre etiqueta,ROUND(SUM(f.ingreso_neto_cent)/100.0,2) valor'+BASE+'GROUP BY ca.canal_sk ORDER BY valor DESC LIMIT 1','Ingreso neto','canal','SUM(neto)')
add('margen_canales','SELECT ca.nombre||" / "||t.anio_mes etiqueta, ROUND(SUM(f.margen_bruto_cent)/100.0,2) valor'+BASE+'WHERE ca.nombre IN (:canal1,:canal2) AND t.anio_mes IN (SELECT DISTINCT anio_mes FROM dim_tiempo ORDER BY anio_mes DESC LIMIT 3) GROUP BY ca.nombre,t.anio_mes ORDER BY t.anio_mes,ca.nombre','Margen bruto','canal y mes','SUM(margen), tres meses disponibles',('canal1','canal2'))
add('producto_lider','SELECT p.nombre etiqueta,ROUND(SUM(f.ingreso_neto_cent)/100.0,2) valor'+BASE+'WHERE p.categoria=:categoria AND t.anio_mes=:periodo GROUP BY p.producto_sk ORDER BY valor DESC LIMIT 1','Ingreso neto','producto','SUM(neto) por categoría y periodo',('categoria','periodo'))
add('productos_deterioro','WITH z AS (SELECT p.nombre, SUM(CASE WHEN t.mes=12 THEN f.ingreso_neto_cent ELSE 0 END) actual,SUM(CASE WHEN t.mes=11 THEN f.ingreso_neto_cent ELSE 0 END) anterior,SUM(CASE WHEN t.mes=12 THEN f.margen_bruto_cent ELSE 0 END) margen_actual,SUM(CASE WHEN t.mes=11 THEN f.margen_bruto_cent ELSE 0 END) margen_anterior'+BASE+' GROUP BY p.nombre) SELECT nombre etiqueta,ROUND((actual-anterior)/100.0,2) valor FROM z WHERE actual<anterior AND margen_actual<margen_anterior ORDER BY valor','Variación ingresos','producto','Diciembre contra noviembre')
add('sucursales_crecimiento','WITH z AS (SELECT s.nombre,SUM(CASE WHEN t.mes=12 THEN f.ingreso_neto_cent ELSE 0 END) na,SUM(CASE WHEN t.mes=11 THEN f.ingreso_neto_cent ELSE 0 END) np,SUM(CASE WHEN t.mes=12 THEN f.margen_bruto_cent ELSE 0 END) ma,SUM(CASE WHEN t.mes=11 THEN f.margen_bruto_cent ELSE 0 END) mp'+BASE+'GROUP BY s.nombre) SELECT nombre etiqueta, ROUND((na-np)/100.0,2) valor FROM z WHERE na>np AND np>0 AND na>0 AND ma*1.0/na<mp*1.0/np ORDER BY valor DESC','Variación ingresos y tasa margen','sucursal','Crecimiento de ventas con caída de margen porcentual')
add('segmentos_canales','SELECT cl.segmento||" / "||ca.nombre etiqueta,ROUND(SUM(f.margen_bruto_cent)/100.0,2) valor'+BASE+'GROUP BY cl.segmento,ca.nombre ORDER BY valor DESC LIMIT 10','Margen bruto','segmento y canal','SUM(margen) por segmento histórico/canal')
add('periodo_sin_datos','SELECT t.anio_mes etiqueta,ROUND(SUM(f.ingreso_neto_cent)/100.0,2) valor'+BASE+'WHERE t.anio_mes=:periodo GROUP BY t.anio_mes','Ingreso neto','mes','SUM(neto)',('periodo',))
