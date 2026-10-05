import pytest

from app.partido.estados import *
from app.partido.motor import MotorPartido, T


def crear_estado_prueba():
    cancha = Cancha(
        ancho=100,
        alto=50,
        arco_izquierdo=Arco(
            poste_superior=Coordenada(0, 20),
            poste_inferior=Coordenada(0, 30)),
        arco_derecho=Arco(
            poste_superior=Coordenada(100, 20),
            poste_inferior=Coordenada(100, 30)))

    jugador_1 = JugadorEstado(
        id_jugador=1,
        id_equipo=10,
        id_usuario=1,
        posicion=Coordenada(49, 25),
        control=50,
        agilidad=60,
        fuerza=70,
        poder=80,
        velocidad=40)

    jugador_2 = JugadorEstado(
        id_jugador=2,
        id_equipo=20,
        id_usuario=2,
        posicion=Coordenada(80, 25),
        control=60,
        agilidad=50,
        fuerza=80,
        poder=70,
        velocidad=50)

    return EstadoPartido(
        id_usuario_izquierdo=1,
        id_usuario_derecho=2,
        id_equipo_izquierdo=10,
        id_equipo_derecho=20,
        cancha=cancha,
        jugadores={
            (1, 1): jugador_1,
            (2, 2): jugador_2,
        },
        comportamientos={
            (1, 1): """
def comportamiento(primitivas):
    pass
""",
            (2, 2): """
def comportamiento(primitivas):
    pass
"""
        },
        pelota=PelotaEstado(posicion=Coordenada(50, 25), velocidad=Coordenada(0, 0)))


def test_tick_avanza_el_tiempo():
    estado = crear_estado_prueba()
    motor = MotorPartido(estado)

    tiempo_inicial = estado.tiempo

    estado, _, _ = motor.tick()

    assert estado.tiempo == pytest.approx(tiempo_inicial + T)


def test_tick_devuelve_el_estado():
    estado = crear_estado_prueba()
    motor = MotorPartido(estado)

    resultado_estado, _, _ = motor.tick()

    assert resultado_estado is estado


def test_tick_devuelve_estado_de_todos_los_jugadores():
    estado = crear_estado_prueba()
    motor = MotorPartido(estado)

    estado, estados_jugadores, _ = motor.tick()

    assert len(estados_jugadores) == 2
    assert (1, 1) in estados_jugadores
    assert (2, 2) in estados_jugadores


def test_tick_jugador_quieto():
    estado = crear_estado_prueba()
    motor = MotorPartido(estado)

    estado, estados_jugadores, _ = motor.tick()

    assert estados_jugadores[(1, 1)] == "quieto"
    assert estados_jugadores[(2, 2)] == "quieto"
