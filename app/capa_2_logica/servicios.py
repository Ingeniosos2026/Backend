import re
from typing import Protocol
from pwdlib import PasswordHash

from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador as JugadorModelo
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento as ComportamientoModelo
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo as EquipoModelo
from app.capa_0_definicion_bd.models.partidos_modelos import Partido as PartidoModelo, TipoPartido, EstadoPartido
from sqlalchemy.exc import IntegrityError
from .errores import *
from .resultados import *

password_hash = PasswordHash.recommended()

class _RepoUsuariosProtocol(Protocol):
    def crear (self, usuario: UsuarioModelo) -> UsuarioModelo: ...
    def obtener_por_email(self, email: str) -> UsuarioModelo | None: ...
    def obtener_por_id(self, id_usuario: int) -> UsuarioModelo | None: ...

class _RepoJugadoresProtocol(Protocol):
    def crear(self, jugador: JugadorModelo) -> JugadorModelo: ...
    def obtener_por_id(self, id_jugador: int) -> JugadorModelo | None: ...

class _RepoComportamientosProtocol(Protocol):
    def obtener_comportamiento_por_id_y_usuario(self, comp_id: int, usuario_id: int) -> ComportamientoModelo | None: ...

class _RepoPartidosProtocol(Protocol):
    def crear(self, partido: PartidoModelo) -> PartidoModelo: ...

class _RepoEquiposProtocol(Protocol):
    def crear(self, equipo: EquipoModelo) -> EquipoModelo: ...
    def obtener_por_id(self, id_equipo: int) -> EquipoModelo | None: ...
    def agregar_jugador(self, equipo: EquipoModelo, jugador: JugadorModelo) -> EquipoModelo: ...

class Servicios:
    """" Servicios que implementan la logica del juego """

    def __init__(self, usuarios: _RepoUsuariosProtocol, jugadores: _RepoJugadoresProtocol = None, comportamientos: _RepoComportamientosProtocol = None, partidos: _RepoPartidosProtocol = None, equipos: _RepoEquiposProtocol = None):
        self.usuarios = usuarios
        self.jugadores = jugadores
        self.comportamientos = comportamientos
        self.partidos = partidos
        self.equipos = equipos
    
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
    
    def crear_jugador(self, usuario_id: int, nombre: str, power: int, agility: int, control: int, speed: int, strength: int) -> CrearJugadorResultado:
        stats = [power, agility, control, speed, strength]
        
        if any(s < 20 or s > 100 for s in stats):
            raise DatosInvalidos()
        
        if sum(stats) != 300:
            raise DatosInvalidos()

        nuevo_jugador = JugadorModelo(
            id_usuario=usuario_id,
            nombre_jugador=nombre,
            poder=power,
            agilidad=agility,
            control=control,
            velocidad=speed,
            fuerza=strength
        )
        
        try:
            jugador = self.jugadores.crear(nuevo_jugador)
            return CrearJugadorResultado(jugador=jugador)
        except IntegrityError:
            raise DatosInvalidos() # so el usuario_id no existe en la bd, se dispara el error

    def obtener_comportamiento(self, usuario_id: int, comp_id: int) -> ObtenerComportamientoResultado:
        comportamiento = self.comportamientos.obtener_comportamiento_por_id_y_usuario(comp_id, usuario_id)
        
        if comportamiento is None:
            raise ComportamientoNoEncontrado()
            
        return ObtenerComportamientoResultado(comportamiento=comportamiento)

    def crear_amistoso(self, usuario_id: int, id_equipo: int, duracion: int) -> CrearPartidoResultado:
        if duracion <= 0:
            raise DatosInvalidos()

        equipo = self.equipos.obtener_por_id(id_equipo)
        if equipo is None:
            raise EquipoNoEncontrado()

        if equipo.id_usuario != usuario_id:
            raise EquipoNoEncontrado()

        nuevo_partido = PartidoModelo(
            id_usuario_1=usuario_id,
            id_usuario_2=None,
            id_equipo_1=id_equipo,
            id_equipo_2=None,
            duracion_partido=duracion,
            tipo_partido=TipoPartido.AMISTOSO,
            estado_partido=EstadoPartido.DISPONIBLE
        )

        partido = self.partidos.crear(nuevo_partido)
        return CrearPartidoResultado(partido=partido)

    def crear_equipo(self, usuario_id: int) -> CrearEquipoResultado:
        nuevo_equipo = EquipoModelo(
            id_usuario=usuario_id
        )

        usuario = self.usuarios.obtener_por_id(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado()
        equipo = self.equipos.crear(nuevo_equipo)
        return CrearEquipoResultado(equipo=equipo)

    def agregar_jugador_a_equipo(self, usuario_id: int, id_equipo: int, id_jugador: int) -> CrearEquipoResultado:
        equipo = self.equipos.obtener_por_id(id_equipo)
        if equipo is None:
            raise EquipoNoEncontrado()
        if equipo.id_usuario != usuario_id:
            raise UsuarioNoEncontrado()

        jugador = self.jugadores.obtener_por_id(id_jugador)
        if jugador is None:
            raise JugadorNoEncontrado()

        equipo_actualizado = self.equipos.agregar_jugador(equipo, jugador)
        return CrearEquipoResultado(equipo=equipo_actualizado)