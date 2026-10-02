from pydantic import BaseModel
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion

class CrearAmistoso(BaseModel):
    jugadores: list[int]
    duracion: int
    formacion: Formacion