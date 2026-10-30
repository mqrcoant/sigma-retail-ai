"""Modelo de dominio OO; ZODB conserva el grafo de objetos cuando se instala."""
from dataclasses import dataclass,field
from datetime import datetime,timezone
from uuid import uuid4

def uid():return str(uuid4())
@dataclass
class Usuario:
 nombre:str
 id:str=field(default_factory=uid)
@dataclass
class Intencion:
 codigo:str
 metrica:str
 dimension:str
 filtros:dict=field(default_factory=dict)
@dataclass
class Pregunta:
 texto:str
 intencion:Intencion
 id:str=field(default_factory=uid)
 fecha:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())
@dataclass
class ReglaValidacion:
 nombre:str
 aprobada:bool
 detalle:str
 def verificar(self,contexto):return self.aprobada
@dataclass
class FuenteDato:
 tablas:list
 plantilla:str
@dataclass
class ConsultaAnalitica:
 plantilla:str
 parametros:dict
 sql:str
 def validar(self):
  if not self.sql.lstrip().upper().startswith('SELECT') and not self.sql.lstrip().upper().startswith('WITH'):raise ValueError('Consulta no autorizada')
  if ';' in self.sql.strip().rstrip(';'):raise ValueError('Múltiples sentencias no autorizadas')
  return True
@dataclass
class ResultadoConsulta:
 filas:list
 duracion_ms:float
 reglas:list=field(default_factory=list)
@dataclass
class RespuestaAgente:
 texto:str
 fuente:FuenteDato|None
 advertencias:list=field(default_factory=list)
@dataclass
class Sesion:
 usuario:Usuario
 id:str=field(default_factory=uid)
 historial:list=field(default_factory=list)
 def registrar(self,pregunta,consulta,resultado,respuesta):
  self.historial.append({'pregunta':pregunta,'consulta':consulta,'resultado':resultado,'respuesta':respuesta})
@dataclass
class AgenteAnalitico:
 nombre:str='SIGMA Retail AI'
 version:str='1.0'
 def responder(self,texto,sesion,funcion):return funcion(texto,sesion)

@dataclass
class ReglaSoloLectura(ReglaValidacion):
 def verificar(self,contexto):
  sql=contexto.get('sql','').lstrip().upper()
  return sql.startswith(('SELECT ', 'WITH ')) and ';' not in sql.strip().rstrip(';')

@dataclass
class ReglaFilasNoNegativas(ReglaValidacion):
 def verificar(self,contexto):
  return contexto.get('num_filas',0)>=0
