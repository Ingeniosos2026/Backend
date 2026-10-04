import pytest

from app.partido.ejecutar_comportamiento import ejecutar_comportamiento
from app.partido.estados import (Arco, Cancha, Coordenada, EstadoPartido, JugadorEstado, PelotaEstado)


def crear_estado_partido():
    cancha = Cancha(
        ancho=100,
        alto=50,
        arco_izquierdo=Arco(
            poste_superior=Coordenada(0, 20),
            poste_inferior=Coordenada(0, 30),
        ),
        arco_derecho=Arco(
            poste_superior=Coordenada(100, 20),
            poste_inferior=Coordenada(100, 30),
        ),
    )
    jugador_actual = JugadorEstado(
        id_jugador=1,
        id_equipo=10,
        id_usuario=1,
        posicion=Coordenada(49, 25),
        control=50,
        agilidad=60,
        fuerza=70,
        poder=80,
        velocidad=40,
    )
    compañero = JugadorEstado(
        id_jugador=2,
        id_equipo=10,
        id_usuario=1,
        posicion=Coordenada(30, 25),
        control=60,
        agilidad=50,
        fuerza=80,
        poder=60,
        velocidad=50,
    )

    return EstadoPartido(
        id_usuario_izquierdo=1,
        id_usuario_derecho=2,
        id_equipo_izquierdo=10,
        id_equipo_derecho=20,
        cancha=cancha,
        jugadores={(1, 1): jugador_actual, (1, 2): compañero},
        comportamientos={},
        pelota=PelotaEstado(
            posicion=Coordenada(50, 25),
            velocidad=Coordenada(0, 0),
        ),
    )


def test_ejecutar_comportamiento_corre_hacia_un_companero():
    estado = crear_estado_partido()
    jugador = estado.jugadores[(1, 1)]
    codigo = """
def comportamiento(primitivas):
    compañero = primitivas.direccionCompañeros()[0]
    primitivas.correr(compañero)
"""

    ejecutar_comportamiento(estado, jugador, codigo)

    assert jugador.destino == estado.jugadores[(1, 2)].posicion


def test_ejecutar_comportamiento_patea_la_pelota():
    estado = crear_estado_partido()
    jugador = estado.jugadores[(1, 1)]
    codigo = """
def comportamiento(primitivas):
    primitivas.patear(primitivas.direccionArcoRival())
"""

    ejecutar_comportamiento(estado, jugador, codigo)

    assert estado.pelota.velocidad.x > 0
    assert estado.pelota.velocidad.y == pytest.approx(0)
    assert jugador.ultimo_pateo == estado.tiempo


def test_ejecutar_comportamiento_invalido_sin_funcion_comportamiento():
    estado = crear_estado_partido()
    jugador = estado.jugadores[(1, 1)]
    codigo = "def otra_funcion(primitivas): pass"

    with pytest.raises(ValueError, match="debe definir una funcion"):
        ejecutar_comportamiento(estado, jugador, codigo)


def test_ejecutar_comportamiento_ejecuta_la_funcion_definida():
    estado = crear_estado_partido()
    jugador = estado.jugadores[(1, 1)]
    codigo = """
def comportamiento(primitivas):
    primitivas.correr(primitivas.direccionPelota())
"""

    resultado = ejecutar_comportamiento(estado, jugador, codigo)

    assert resultado is None
    assert jugador.destino == estado.pelota.posicion