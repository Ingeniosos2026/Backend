from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador
from app.capa_0_definicion_bd.models.equipos_jugadores_modelos import EstadoJugador, EquipoJugador
from app.partido.inicializacion import crear_jugadores_estado, obtener_posiciones_formacion, crear_cancha
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion


def test_crear_jugadores_estado_selecciona_titulares_y_suplentes():
    jugadores = [EquipoJugador(
        jugador=Jugador(
            id_jugador=jugador_id,
            id_usuario=1,
            nombre_jugador=f"Jugador {jugador_id}",
            control=60,
            agilidad=60,
            fuerza=60,
            poder=60,
            velocidad=60,
        ),
        estado=estado,
        comportamiento=Comportamiento(codigo=f"comportamiento_{jugador_id}"),
    )
    for jugador_id, estado in [
        (4, EstadoJugador.SUPLENTE),
        (5, EstadoJugador.SUPLENTE),
        (6, EstadoJugador.SUPLENTE),
        (1, EstadoJugador.TITULAR),
        (2, EstadoJugador.TITULAR),
        (3, EstadoJugador.TITULAR)
    ]
]
    posiciones = obtener_posiciones_formacion(Formacion.OFENSIVA, "izquierdo", crear_cancha())
    jugadores_estado, suplentes_estado, comportamientos = crear_jugadores_estado(jugadores, id_usuario=1, id_equipo=10, posiciones=posiciones)

    assert len(suplentes_estado) == 3
    assert len(jugadores_estado) == 3
    assert len(comportamientos) == 6
    
    for jugador_id in [1, 2, 3]:
        clave = (1, jugador_id)
        assert clave in jugadores_estado
        assert clave not in suplentes_estado
    
    for jugador_id in [4, 5, 6]:
        clave = (1, jugador_id)
        assert clave in suplentes_estado
        assert clave not in jugadores_estado



def test_comportamiento_de_jugador_se_resuelve_por_equipo():
    jugadores = [
        Jugador(
            id_jugador=id_jugador,
            id_usuario=1,
            nombre_jugador=f" Messi {id_jugador}",
            control=60,
            agilidad=60,
            fuerza=60,
            poder=60,
            velocidad=60)
        for id_jugador in range(1, 7)
    ]
    equipos_jugadores_partido_1 = [
        EquipoJugador(jugador=jugador, estado=(EstadoJugador.TITULAR if jugador.id_jugador <= 3 else EstadoJugador.SUPLENTE), comportamiento=Comportamiento(
                codigo="comportamiento_partido_1" if jugador.id_jugador == 1 else "comportamiento_compartido"
            ))
        for jugador in jugadores
    ]
    equipos_jugadores_partido_2 = [
        EquipoJugador(jugador=jugador, estado=(EstadoJugador.TITULAR if jugador.id_jugador <= 3 else EstadoJugador.SUPLENTE), comportamiento=Comportamiento(
                codigo="comportamiento_partido_2" if jugador.id_jugador == 1 else "comportamiento_compartido"
            ))
        for jugador in jugadores
    ]
    posiciones = obtener_posiciones_formacion(Formacion.OFENSIVA, "izquierdo", crear_cancha())

    _, _, comportamientos_partido_1 = crear_jugadores_estado(equipos_jugadores_partido_1, id_usuario=1, id_equipo=10, posiciones=posiciones)
    _, _, comportamientos_partido_2 = crear_jugadores_estado(equipos_jugadores_partido_2, id_usuario=2, id_equipo=11, posiciones=posiciones)

    assert comportamientos_partido_1[(1, 1)] == "comportamiento_partido_1"
    assert comportamientos_partido_2[(2, 1)] == "comportamiento_partido_2"

    assert len(comportamientos_partido_1) == 6
    assert len(comportamientos_partido_2) == 6
