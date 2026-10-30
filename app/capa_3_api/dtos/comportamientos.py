from pydantic import BaseModel

class CrearComportamiento(BaseModel):
    nombre: str
    codigo: str