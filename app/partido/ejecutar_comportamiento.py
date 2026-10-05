from .estados import EstadoPartido, JugadorEstado
from .primitivas import Primitivas
from .evento import EventoJugador

def ejecutar_comportamiento(estado: EstadoPartido, jugador: JugadorEstado, codigo: str, eventos: list[EventoJugador]) -> None:
    primitivas = Primitivas(
        estado=estado,
        id_usuario=jugador.id_usuario,
        id_jugador=jugador.id_jugador,
        eventos=eventos
    )

## esto necesitaria algun tipo de aislamiento cuando implementemos crear_comportamiento
    entorno = {}
    exec(codigo, entorno)

    comportamiento = entorno.get("comportamiento")

    if comportamiento is None:
        raise ValueError(
            "El comportamiento debe definir una funcion llamada 'comportamiento(primitivas)'"
        )

    comportamiento(primitivas)