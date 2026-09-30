import re
from typing import Protocol
from pwdlib import PasswordHash

from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo
from .errores import *
from .resultados import *

password_hash = PasswordHash.recommended()

class _RepoUsuariosProtocol(Protocol):
    def crear (self, usuario: UsuarioModelo) -> UsuarioModelo: ...
    def obtener_por_email(self, email: str) -> UsuarioModelo | None: ...


class Servicios:
    """" Servicios que implementan la logica del juego """


    def __init__(self, usuarios: _RepoUsuariosProtocol):
        self.usuarios = usuarios

    
    def email_valido(self, email: str) -> bool:
        patron = r"^[a-zA-Z0-9._%+-]+@(gmail|hotmail|outlook)\.com$"
        return re.match(patron, email) is not None
    
    def crear_usuario(self, email: str, nombre: str, id_avatar: int, contraseña: str, nombre_club: str) -> CrearUsuarioResultado:
        
        if not nombre.strip():
            raise DatosInvalidos

        if not contraseña.strip():
            raise DatosInvalidos

        if not nombre_club.strip():
            raise DatosInvalidos

        if not self.email_valido(email):
            raise DatosInvalidos
        
        if self.usuarios.obtener_por_email(email) is not None:
            raise EmailRegistrado
        

        hash_contraseña = password_hash.hash(contraseña)

        nuevo_usuario = UsuarioModelo(
            email=email,
            nombre=nombre,
            id_avatar=id_avatar,
            contraseña=hash_contraseña,
            nombre_club=nombre_club
        )

        usuario = self.usuarios.crear(nuevo_usuario)

        return CrearUsuarioResultado(usuario=usuario)

    def login_usuario(self, email: str, contraseña: str) -> UsuarioModelo:
        usuario = self.usuarios.obtener_por_email(email)
        if usuario is None:
            raise CredencialesInvalidas
        
        if not password_hash.verify(contraseña, usuario.contraseña):
            raise CredencialesInvalidas
        
        return usuario