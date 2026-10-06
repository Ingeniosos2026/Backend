from pydantic import BaseModel

class CrearJugador(BaseModel):
    nombre: str
    power: int
    agility: int
    control: int
    speed: int
    strength: int