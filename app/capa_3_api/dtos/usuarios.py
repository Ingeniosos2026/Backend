from pydantic import BaseModel


class CrearUsuario(BaseModel):
    nombre: str
    email: str
    contraseña: str
    avatar: int
    club: str

class LoginUsuario(BaseModel):
    email: str
    contraseña: str