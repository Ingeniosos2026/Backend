from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo
from dataclasses import dataclass



@dataclass(slots=True)
class CrearUsuarioResultado:
    usuario: UsuarioModelo

