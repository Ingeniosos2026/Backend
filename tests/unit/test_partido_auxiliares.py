import pytest
from app.partido.estados import *

from app.partido.auxiliares import *


def test_calcular_distancia():
    a = Coordenada(0, 0)
    b = Coordenada(3, 4)

    resultado = calcular_distancia(a, b)

    assert resultado == 5


def test_calcular_distancia_misma_posicion():
    a = Coordenada(10, 20)
    b = Coordenada(10, 20)

    resultado = calcular_distancia(a, b)

    assert resultado == 0


def test_calcular_direccion():
    origen = Coordenada(0, 0)
    destino = Coordenada(3, 4)

    resultado = calcular_direccion(origen, destino)

    assert resultado.x == pytest.approx(0.6)
    assert resultado.y == pytest.approx(0.8)


def test_calcular_direccion_misma_posicion():
    origen = Coordenada(10, 20)
    destino = Coordenada(10, 20)

    resultado = calcular_direccion(origen, destino)

    assert resultado.x == 0
    assert resultado.y == 0


def test_calcular_alcance():
    resultado = calcular_alcance(50)

    assert resultado == 1.5


def test_calcular_tiempo_pateo():
    resultado = calcular_tiempo_pateo(100)

    assert resultado == pytest.approx(0.5)


def test_calcular_potencia():
    resultado = calcular_potencia(100)

    assert resultado == 10.0


def test_calcular_velocidad():
    resultado = calcular_velocidad(50)

    assert resultado == 4.0


def test_obtener_jugador():
    jugador1 = JugadorEstado(
        id_jugador=1,
        id_equipo=10,
        posicion=Coordenada(20, 25),
        control=50,
        agilidad=60,
        fuerza=70,
        poder=80,
        velocidad=40)

    jugador2 = JugadorEstado(
        id_jugador=1,
        id_equipo=11,
        posicion=Coordenada(20, 25),
        control=50,
        agilidad=60,
        fuerza=70,
        poder=80,
        velocidad=40)

    cancha = Cancha(
        ancho=100,
        alto=50,
        arco_izquierdo=Arco(poste_superior=Coordenada(0, 20), poste_inferior=Coordenada(0, 30)), 
        arco_derecho=Arco(poste_superior=Coordenada(100, 20), poste_inferior=Coordenada(100, 30)))

    pelota = PelotaEstado(posicion=Coordenada(50, 25), velocidad=Coordenada(0, 0))

    estado = EstadoPartido(
        id_usuario_izquierdo=1,
        id_usuario_derecho=2,
        id_equipo_izquierdo=10,
        id_equipo_derecho=20,
        cancha=cancha,
        jugadores={(1, 1): jugador1, (2, 1): jugador2},
        pelota=pelota)

    resultado = obtener_jugador(estado, id_usuario=1, id_jugador=1)

    assert resultado == jugador1


def test_posicion_valida_dentro_de_cancha():
    cancha = Cancha(
        ancho=100,
        alto=50,
        arco_izquierdo=Arco(poste_superior=Coordenada(0, 20), poste_inferior=Coordenada(0, 30)),
        arco_derecho=Arco(poste_superior=Coordenada(100, 20), poste_inferior=Coordenada(100, 30)))

    posicion = Coordenada(50, 25)

    assert posicion_valida(posicion, cancha) is True
