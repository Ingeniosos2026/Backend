from pydantic import BaseModel
from typing import Optional

class CrearLiga(BaseModel):
    nombre: str 
    contraseña: Optional[str] = None
    min_jugadores: int 
    max_jugadores: int 
    duracion_partido: int 

class UnirseLiga(BaseModel): # esto es para evitar que se mande la contraseña en la url por obvias razones.......
    contraseña: Optional[str] = None
