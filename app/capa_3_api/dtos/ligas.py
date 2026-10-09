from pydantic import BaseModel

class CrearLiga(BaseModel):
    nombre: str 
    contraseña: str 
    min_jugadores: int 
    max_jugadores: int 
    duracion_partido: int 
