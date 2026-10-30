from artifact_tool import Workbook,SpreadsheetFile
import csv
from pathlib import Path
r=Path(__file__).resolve().parent
with (r/'evidence'/'resultados_pruebas.csv').open(encoding='utf8') as f:rows=list(csv.reader(f))
w=Workbook.create();s=w.worksheets.add('Matriz de pruebas');s.get_range('A1:J21').values=rows
s.get_range('A1:J1').format={'fill':'#173B59','font':{'bold':True,'color':'#FFFFFF'},'row_height':38,'wrap_text':True}
s.get_range('A:A').format.column_width=9
s.get_range('B:B').format.column_width=63
s.get_range('C:C').format.column_width=30
s.get_range('D:G').format.column_width=20
s.get_range('H:H').format.column_width=14
s.get_range('I:I').format.column_width=60
s.get_range('J:J').format.column_width=70
s.get_range('A2:J21').format.row_height=44
s.get_range('A2:J21').format.wrap_text=True
s.freeze_panes.freeze_rows(1)
info=w.worksheets.add('Criterios')
info.get_range('A1:B10').values=[['CRITERIO','DEFINICIÓN'],['Datos','Datos 2026 sintéticos (semilla 42026)'],['Estados','ok: filas; sin_datos: consulta válida vacía; rechazada: control de límites'],['Control 1','PRAGMA foreign_key_check = 0 incidencias'],['Control 2','SUM(neto) = total de origen'],['Control 3','COUNT(lineas) = filas de origen'],['SCD2','Segmento histórico vigente en la fecha del hecho'],['Ticket','SUM(neto)/COUNT(DISTINCT ticket_id)'],['LLM','No implementado; interpretación determinista local'],['Entorno','ZODB y Streamlit requieren instalación para validar visualmente']]
info.get_range('A1:B1').format={'fill':'#173B59','font':{'bold':True,'color':'#FFFFFF'}}
info.get_range('A:A').format.column_width=25;info.get_range('B:B').format.column_width=85
SpreadsheetFile.export_xlsx(w).save(str(r/'EquipoXX_Pruebas.xlsx'))
print('Excel creado')
