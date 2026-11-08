from app.partido.comportamientos import comportamiento_atacar, comportamiento_defender
from app.partido.estados import Arco, Cancha, Coordenada, EstadoPartido,JugadorEstado, PelotaEstado
from app.partido.ejecutar_comportamiento_dt import ejecutar_comportamiento_dt

def crear_estado_partido():
    cancha = Cancha(ancho=100,alto=50,
        arco_izquierdo=Arco(
            poste_superior=Coordenada(0, 20),
            poste_inferior=Coordenada(0, 30)),
        arco_derecho=Arco(
            poste_superior=Coordenada(100, 20),
            poste_inferior=Coordenada(100, 30)),
    )
    jugador = JugadorEstado(
        id_jugador=1,
        id_equipo=10,
        id_usuario=1,
        nombre="messi",
        posicion=Coordenada(20, 25),
        control=50,
        agilidad=60,
        fuerza=70,
        poder=80,
        velocidad=40,
        destino=Coordenada(30, 25)
    )
    jugador_2 = JugadorEstado(
        id_jugador=2,
        id_equipo=10,
        id_usuario=1,
        nombre="julian",
        posicion=Coordenada(40, 25),
        control=60,
        agilidad=50,
        fuerza=80,
        poder=70,
        velocidad=50
    )
    suplente = JugadorEstado(
        id_jugador=3,
        id_equipo=10,
        id_usuario=1,
        nombre="paredes",
        posicion=Coordenada(10, 25),
        control=70,
        agilidad=40,
        fuerza=60,
        poder=90,
        velocidad=60,
        destino=Coordenada(15, 25)
    )
    rival = JugadorEstado(
        id_jugador=4,
        id_equipo=20,
        id_usuario=2,
        nombre="cristiano",
        posicion=Coordenada(80, 25),
        control=70,
        agilidad=40,
        fuerza=60,
        poder=90,
        velocidad=60
    )

    return EstadoPartido(
        id_usuario_izquierdo=1,
        id_usuario_derecho=2,
        id_equipo_izquierdo=10,
        id_equipo_derecho=20,
        cancha=cancha,
        jugadores={(1, 1): jugador, (1, 2): jugador_2, (2, 4): rival},
        suplentes={(1, 3): suplente},
        comportamientos={
            (1, 1): comportamiento_defender,
            (1, 2): comportamiento_defender,
            (2, 4): comportamiento_defender,
        },
        codigo_dt={},
        dt_activo={1: False, 2: False},
        pelota=PelotaEstado(
            posicion=Coordenada(50, 25),
            velocidad=Coordenada(0, 0)
        ))


def test_ejecutar_comportamiento_dt_cambia_jugador_con_primitiva():
    estado = crear_estado_partido()
    estado.en_pausa = True
    jugador_que_sale = estado.jugadores[(1, 1)]
    suplente_que_entra = estado.suplentes[(1, 3)]
    codigo = """def comportamiento(primitivas): primitivas.cambiar_jugador()"""

    ejecutar_comportamiento_dt(estado, 1, codigo)

    assert (1, 1) not in estado.jugadores
    assert estado.jugadores[(1, 3)] is suplente_que_entra
    assert estado.suplentes[(1, 1)] is jugador_que_sale
    assert suplente_que_entra.posicion == jugador_que_sale.posicion
    assert suplente_que_entra.destino is None


def test_ejecutar_comportamiento_dt_cambia_comportamiento_con_primitiva():
    estado = crear_estado_partido()
    codigo = """def comportamiento(primitivas): primitivas.cambiar_comportamiento_ataque()"""

    ejecutar_comportamiento_dt(estado, 1, codigo)

    assert estado.comportamientos[(1, 1)] == comportamiento_atacar
    assert estado.comportamientos[(1, 2)] == comportamiento_atacar
    assert estado.comportamientos[(2, 4)] == comportamiento_defender
