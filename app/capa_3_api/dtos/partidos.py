from pydantic import BaseModel
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion


class JugadorConComportamiento(BaseModel):
    id_jugador: int
    id_comportamiento: int


class CrearAmistoso(BaseModel):
    jugadores: list[JugadorConComportamiento]
    duracion: int
    formacion: Formacion

class UnirseAmistoso(BaseModel):
    jugadores: list[JugadorConComportamiento]
    formacion: Formacion