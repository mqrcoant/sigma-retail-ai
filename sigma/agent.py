import re,sqlite3,time,unicodedata
from .catalog import T
from .objects import *
from .generate import DB
class ConsultaNoSoportada(Exception):pass

def normalizar(text):return ''.join(c for c in unicodedata.normalize('NFD',text.lower()) if unicodedata.category(c)!='Mn')
def interpretar(texto):
 q=normalizar(texto)
 if any(x in q for x in ['drop ','delete ','update ','alter ','truncate ','elimina la tabla','borra la tabla','modifica la tabla']):raise ConsultaNoSoportada('Operación no autorizada: solo lectura analítica.')
 if any(x in q for x in ['salario','nomina','empleados','inventario','clima','prediccion']):raise ConsultaNoSoportada('Fuera del alcance: el Data Mart contiene ventas y rentabilidad, no esa dimensión.')
 if any(x in q for x in ['proveedor','pais','vendedor']):raise ConsultaNoSoportada('Dimensión inexistente en el esquema aprobado.')
 if 'mejor canal' in q and not any(x in q for x in ['ingreso','margen','ticket','cantidad']):raise ConsultaNoSoportada('Pregunta ambigua: indique ingreso neto, margen bruto, cantidad o ticket promedio.')
 params={}
 if 'periodo sin datos' in q or '2030-01' in q:return 'periodo_sin_datos',{'periodo':'2030-01'}
 if 'compare' in q and 'canal' in q:
  opciones=['Tienda','Web','Marketplace'];seleccion=[x for x in opciones if x.lower() in q]
  if len(seleccion)<2:raise ConsultaNoSoportada('Indique dos canales diferentes: Tienda, Web o Marketplace.')
  return 'margen_canales',{'canal1':seleccion[0],'canal2':seleccion[1]}
 if 'producto' in q and ('lider' in q or 'lidera' in q):
  categorias=['Informática','Accesorios','Audio','Televisores','Móviles'];cat=next((x for x in categorias if normalizar(x) in q),None)
  periodo=re.search(r'2026-(0[1-9]|1[0-2])',q)
  if not cat or not periodo:raise ConsultaNoSoportada('Para producto líder indique categoría y periodo AAAA-MM.')
  return 'producto_lider',{'categoria':cat,'periodo':periodo.group(0)}
 if 'deterior' in q or ('productos' in q and 'caida' in q):return 'productos_deterioro',{}
 if 'sucursal' in q and ('increment' in q or 'creci' in q):return 'sucursales_crecimiento',{}
 if 'segment' in q and 'canal' in q:return 'segmentos_canales',{}
 if 'segment' in q and any(x in q for x in ['reduc','reduj','caida','disminuy']):return 'segmento_caida',{}
 if 'ticket' in q and 'sucursal' in q:return 'sucursal_ticket',{}
 if 'categor' in q and 'margen' in q:return 'categorias_margen',{}
 if 'canal' in q and 'margen' not in q:return 'canal_ventas',{}
 if ('ingreso' in q or 'venta' in q) and any(x in q for x in ['mes','mensual','periodo']):return 'ingreso_mes',{}
 raise ConsultaNoSoportada('No se identificó una consulta admitida. Revise las diez preguntas del catálogo.')
def ejecutar(texto,sesion,db=DB):
 try:codigo,params=interpretar(texto)
 except ConsultaNoSoportada as exc:
  p=Pregunta(texto,Intencion('no_autorizada','N/A','N/A'))
  r=RespuestaAgente(str(exc),None,[str(exc)])
  sesion.registrar(p,None,None,r)
  return {'estado':'rechazada','respuesta':r.texto,'fuente':None,'filas':[],'plantilla':None}
 plantilla=T[codigo]
 if any(x not in params for x in plantilla.parameters):raise ConsultaNoSoportada('Parámetros incompletos')
 consulta=ConsultaAnalitica(codigo,params,plantilla.sql);consulta.validar()
 p=Pregunta(texto,Intencion(codigo,plantilla.metric,plantilla.dimension,params))
 inicio=time.perf_counter()
 con=sqlite3.connect(f'file:{db}?mode=ro',uri=True)
 try:
  con.execute('PRAGMA query_only=ON')
  cur=con.execute(plantilla.sql,params)
  filas=[dict(zip([x[0] for x in cur.description],r)) for r in cur.fetchall()]
 finally:con.close()
 resultado=ResultadoConsulta(filas,round((time.perf_counter()-inicio)*1000,2),[ReglaValidacion('Consulta de solo lectura',True,'SELECT/CTE parametrizada'),ReglaValidacion('Fuente autorizada',True,'Data Mart SQLite')])
 fuente=FuenteDato(['fact_ventas','dim_tiempo','dim_producto','dim_cliente','dim_sucursal','dim_canal'],codigo)
 if filas:
  resumen='; '.join(f"{f['etiqueta']}: {f['valor']}" for f in filas[:12])
  mensaje=f"{plantilla.metric} por {plantilla.dimension}. {resumen}. Regla: {plantilla.rule}. Fuente: Data Mart, plantilla {codigo}. Periodo: 2026 salvo filtros especificados."
  estado='ok'
 else:mensaje=f'Sin registros para los filtros solicitados. No se interpreta la ausencia como cero. Fuente: {codigo}.';estado='sin_datos'
 respuesta=RespuestaAgente(mensaje,fuente,[] if filas else ['No existen observaciones para el filtro.'])
 sesion.registrar(p,consulta,resultado,respuesta)
 return {'estado':estado,'respuesta':mensaje,'fuente':fuente.tablas,'filas':filas,'plantilla':codigo,'sql':plantilla.sql,'parametros':params,'duracion_ms':resultado.duracion_ms}
