from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pypdf import PdfReader,PdfWriter
R=Path(__file__).resolve().parent
out=R/'docs/diagramas.pdf'
c=canvas.Canvas(str(out),pagesize=(595,842))
def title(t):
 c.setFont('Helvetica-Bold',19);c.setFillColor(HexColor('#123B59'));c.drawString(45,786,t)
def node(x,y,w,h,txt,col='#DCECF9'):
 c.setFillColor(HexColor(col));c.setStrokeColor(HexColor('#47799E'));c.roundRect(x,y,w,h,8,fill=1,stroke=1);c.setFillColor(HexColor('#173B59'));c.setFont('Helvetica-Bold',10)
 for i,line in enumerate(txt.split('|')):c.drawCentredString(x+w/2,y+h/2+7-i*14,line)
def edge(x,y,x2,y2):
 c.setStrokeColor(HexColor('#4B6476'));c.setLineWidth(1.5);c.line(x,y,x2,y2)
title('Anexo A | Arquitectura de SIGMA')
node(192,675,210,50,'Usuario | Pregunta gerencial')
node(192,556,210,64,'Agente | Interpretación y validación','#D9EEE7')
node(40,420,225,74,'Data Mart SQLite | Fuente analítica oficial')
node(330,420,225,74,'BDOO ZODB | Sesiones y trazabilidad','#F4E5D7')
node(192,295,210,65,'Streamlit | Respuesta + evidencias')
edge(297,675,297,620);edge(255,556,152,494);edge(340,556,443,494);edge(152,420,245,360);edge(443,420,350,360)
c.setFont('Helvetica',11);c.setFillColor(HexColor('#324B5D'));c.drawString(58,235,'El Data Mart no se copia en ZODB; los objetos registran referencias y resultados.')
c.showPage();title('Anexo B | Modelo dimensional: estrella')
node(182,386,230,100,'fact_ventas | Clave: ticket + línea | Neto, costo, margen, unidades','#D9EEE7')
positions=[(50,650,'dim_tiempo'),(332,650,'dim_producto'),(50,528,'dim_cliente SCD2'),(332,528,'dim_sucursal'),(50,210,'dim_canal'),(332,210,'dim_promocion')]
for x,y,t in positions:
 node(x,y,210,62,t);edge(x+105,y if y>400 else y+62,297,486 if y>400 else 386)
c.setFont('Helvetica',10);c.drawString(50,130,'Relación: una dimensión (1) a muchas líneas de ventas (N).')
c.drawString(50,110,'Claves sustitutas referenciadas por FK; vigencias SCD2 en cliente.')
c.showPage();title('Anexo C | Clases y relaciones OO')
node(180,674,234,60,'Usuario | id, nombre')
node(180,568,234,72,'Sesion | id, historial | registrar()','#F4E5D7')
edge(297,674,297,640)
node(30,420,158,72,'Pregunta | Intencion')
node(218,420,158,72,'ConsultaAnalitica | validar()')
node(406,420,158,72,'ResultadoConsulta | filas, validaciones')
for x in (109,297,485):edge(297,568,x,492)
node(180,281,234,73,'RespuestaAgente | FuenteDato, advertencias','#D9EEE7')
edge(297,420,297,354)
node(180,155,234,66,'AgenteAnalitico | responder()')
edge(297,281,297,221)
c.setFont('Helvetica',10);c.drawString(40,99,'Sesion compone el historial; cada entrada conserva los objetos de ejecución.')
c.showPage();c.save()
writer=PdfWriter()
for p in PdfReader(str(R/'EquipoXX_Informe_Parcial01.pdf')).pages:writer.add_page(p)
for p in PdfReader(str(out)).pages:writer.add_page(p)
with (R/'EquipoXX_Informe_Parcial01_vFinal.pdf').open('wb') as f:writer.write(f)
print('informe final pages',len(writer.pages))
