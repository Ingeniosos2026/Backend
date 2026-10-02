from pydantic import BaseModel

class CrearAmistoso(BaseModel):
    id_equipo: int
    duracion: int