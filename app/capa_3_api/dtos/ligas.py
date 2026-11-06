from pydantic import BaseModel
from typing import Optional
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion
from app.capa_3_api.dtos.partidos import JugadorConComportamiento

class CrearLiga(BaseModel):
    nombre: str 
    contraseña: Optional[str] = None
    min_jugadores: int 
    max_jugadores: int 
    duracion_partido: int 
    jugadores: list[JugadorConComportamiento]
    formacion: Formacion

class UnirseLiga(BaseModel): # esto es para evitar que se mande la contraseña en la url por obvias razones.......
    contraseña: Optional[str] = None
    jugadores: list[JugadorConComportamiento]
    formacion: Formacion

class CambiarAlineacion(BaseModel):
    formacion: Formacion
    jugadores: list[JugadorConComportamiento]