from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador as JugadorModelo
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento as ComportamientoModelo
from dataclasses import dataclass



@dataclass(slots=True)
class CrearUsuarioResultado:
    usuario: UsuarioModelo

@dataclass(slots=True)
class CrearJugadorResultado:
    jugador: JugadorModelo

@dataclass(slots=True)
class ObtenerComportamientoResultado:
    comportamiento: ComportamientoModelo