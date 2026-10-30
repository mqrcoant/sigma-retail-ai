import streamlit as st
from sigma.generate import DB,build
from sigma.agent import ejecutar
from sigma.objects import Sesion,Usuario
from sigma.store import AlmacenObjetos
st.set_page_config(page_title='SIGMA Retail AI',page_icon='📊',layout='wide')
st.title('SIGMA Retail AI · Inteligencia comercial trazable')
st.caption('Prototipo académico — datos sintéticos, Data Mart de solo lectura y objetos persistentes ZODB')
if not DB.exists():build()
@st.cache_resource
def store():return AlmacenObjetos(DB.parent/'sesiones.fs')
if 'id_sesion' not in st.session_state:
 sesion=store().obtener();st.session_state.id_sesion=sesion.id
else:sesion=store().obtener(st.session_state.id_sesion)
ejemplos=['¿Cuál fue el ingreso neto por mes?','¿Cuáles son las cinco categorías con mayor margen bruto?','¿Qué sucursal presenta el ticket promedio más alto?','¿Qué segmento de clientes redujo más su volumen de compra?','¿Qué canal concentra el mayor valor de ventas?','Compare el margen de los canales Tienda y Web durante los últimos tres meses disponibles','¿Qué producto lidera las ventas en la categoría Audio en 2026-06?','¿Qué productos muestran caída de ingresos y margen?','¿Qué sucursales incrementaron ventas pero disminuyeron el margen?','¿Qué segmentos aportan más margen por canal?']
with st.sidebar:
 st.subheader('Catálogo de consultas')
 ejemplo=st.selectbox('Pregunta sugerida',ejemplos)
 st.text('Sesión: '+sesion.id[:8]);st.metric('Interacciones',len(sesion.historial))
pregunta=st.text_area('Consulta de gerencia',value=ejemplo)
if st.button('Consultar Data Mart',type='primary'):
 respuesta=ejecutar(pregunta,sesion)
 store().guardar(sesion)
 st.subheader('Respuesta')
 if respuesta['estado']=='ok':st.success(respuesta['respuesta'])
 else:st.warning(respuesta['respuesta'])
 if respuesta.get('filas'):st.dataframe(respuesta['filas'],use_container_width=True)
 with st.expander('Auditoría: consulta, parámetros y fuentes'):
  st.code(respuesta.get('sql','Consulta no ejecutada'),'sql');st.json({'plantilla':respuesta.get('plantilla'),'parametros':respuesta.get('parametros',{}),'fuentes':respuesta.get('fuente'),'duracion_ms':respuesta.get('duracion_ms')})
with st.expander('Historial de objetos persistidos'):
 for i,reg in enumerate(reversed(sesion.historial)):
  st.write(f"{len(sesion.historial)-i}. {reg['pregunta'].texto} — {reg['respuesta'].texto[:140]}")
