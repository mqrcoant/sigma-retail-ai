"""Persistencia ZODB. Se requiere instalar requirements.txt para ejecutar interfaz."""
from pathlib import Path
from .objects import Sesion,Usuario
class AlmacenObjetos:
 def __init__(self,path):
  from ZODB import DB,FileStorage
  self.storage=FileStorage.FileStorage(str(Path(path)),create=True)
  self.db=DB(self.storage)
 def obtener(self,session_id=None):
  conn=self.db.open()
  try:
   root=conn.root()
   from persistent.mapping import PersistentMapping
   if 'sesiones' not in root:
    import transaction
    root['sesiones']=PersistentMapping();transaction.commit()
   sesiones=root['sesiones']
   if session_id and session_id in sesiones:return sesiones[session_id]
   s=Sesion(Usuario('Gerencia'))
   # Reasignar valor para activar tracking; ZODB debe serializar cambios de objetos dataclass
   sesiones[s.id]=s
   import transaction
   transaction.commit()
   return s
  finally:conn.close()
 def guardar(self,s):
  import transaction
  conn=self.db.open()
  try:
   conn.root()['sesiones'][s.id]=s
   transaction.commit()
  finally:conn.close()
 def cerrar(self):self.db.close();self.storage.close()
