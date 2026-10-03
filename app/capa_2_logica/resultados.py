from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador as JugadorModelo
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo as EquipoModelo
from app.capa_0_definicion_bd.models.partidos_modelos import Partido as PartidoModelo
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

@dataclass(slots=True)
class CrearPartidoResultado:
    partido: PartidoModelo

@dataclass(slots=True)
class CrearEquipoResultado:
    equipo: EquipoModelo