from pydantic import BaseModel


class CrearUsuario(BaseModel):
    email: str
    nombre: str
    id_avatar: int
    contraseña: str
    nombre_club: str