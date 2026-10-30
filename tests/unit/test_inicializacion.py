from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento
from app.capa_0_definicion_bd.models.jugadores_modelos import EstadoJugador, Jugador
from app.partido.inicializacion import crear_jugadores_estado, obtener_posiciones_formacion, crear_cancha
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion


def test_crear_jugadores_estado_selecciona_titulares_y_omite_suplentes():
    jugadores = [Jugador(
            id_jugador=jugador_id,
            id_usuario=1,
            nombre_jugador=f"Jugador {jugador_id}",
            control=60,
            agilidad=60,
            fuerza=60,
            poder=60,
            velocidad=60,
            estado=estado,
            comportamiento=Comportamiento(codigo=f"comportamiento_{jugador_id}"))
        for jugador_id, estado in [
            (4, EstadoJugador.SUPLENTE),
            (5, EstadoJugador.SUPLENTE),
            (6, EstadoJugador.SUPLENTE),
            (1, EstadoJugador.TITULAR),
            (2, EstadoJugador.TITULAR),
            (3, EstadoJugador.TITULAR)]
    ]
    posiciones = obtener_posiciones_formacion(Formacion.OFENSIVA, "izquierdo", crear_cancha())
    jugadores_estado, comportamientos = crear_jugadores_estado(jugadores, id_usuario=1, id_equipo=10, posiciones=posiciones)

    assert set(jugadores_estado) == {(1, 1), (1, 2), (1, 3)}
    assert comportamientos == {
        (1, 1): "comportamiento_1",
        (1, 2): "comportamiento_2",
        (1, 3): "comportamiento_3"
    }
