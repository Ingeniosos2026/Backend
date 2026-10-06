import pytest

from app.partido.estados import *
from app.partido.fisicas import FisicaPartido
from app.partido.auxiliares import *

def crear_estado():
    cancha = Cancha(ancho=100, alto=60,
        arco_izquierdo=Arco(
            poste_superior=Coordenada(0, 35),
            poste_inferior=Coordenada(0, 25)),
        arco_derecho=Arco(
            poste_superior=Coordenada(100, 35),
            poste_inferior=Coordenada(100, 25)))

    jugadores = {(1, 1): JugadorEstado(
            id_jugador=1,
            id_equipo=1,
            id_usuario=1,
            posicion=Coordenada(10, 30),
            control=60,
            agilidad=60,
            fuerza=60,
            poder=60,
            velocidad=60),
        (2, 2): JugadorEstado(
            id_jugador=2,
            id_equipo=2,
            id_usuario=2,
            posicion=Coordenada(90, 30),
            control=60,
            agilidad=60,
            fuerza=60,
            poder=60,
            velocidad=60)}

    pelota = PelotaEstado(posicion=Coordenada(50, 30), velocidad=Coordenada(0, 0))

    return EstadoPartido(
        id_usuario_izquierdo=1,
        id_usuario_derecho=2,
        id_equipo_izquierdo=1,
        id_equipo_derecho=2,
        cancha=cancha,
        jugadores=jugadores,
        comportamientos={},
        pelota=pelota)


def test_actualizar_jugador():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    jugador = estado.jugadores[(1, 1)]
    jugador.destino = Coordenada(20, 30)

    fisica.actualizar_jugadores(1.0)

    assert jugador.posicion.x == 14.4
    assert jugador.posicion.y == 30


def test_jugador_llega_exactamente_al_destino():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    jugador = estado.jugadores[(1, 1)]
    jugador.destino = Coordenada(12, 30)

    fisica.actualizar_jugadores(1.0)

    assert jugador.posicion.x == 12
    assert jugador.posicion.y == 30
    assert jugador.destino is None


def test_jugador_sin_destino_no_se_mueve():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    jugador = estado.jugadores[(1, 1)]

    fisica.actualizar_jugadores(1.0)

    assert jugador.posicion.x == 10
    assert jugador.posicion.y == 30


def test_actualizar_pelota():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    estado.pelota.velocidad = Coordenada(2, 0)

    fisica.actualizar_pelota(1.0)

    assert estado.pelota.posicion.x == 52
    assert estado.pelota.posicion.y == 30


def test_friccion_reduce_velocidad():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    estado.pelota.velocidad = Coordenada(3, 4)

    fisica.aplicar_friccion_pelota(1.0)

    assert estado.pelota.velocidad.x == pytest.approx(1.8)
    assert estado.pelota.velocidad.y == pytest.approx(2.4)


def test_friccion_detiene_pelota():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    estado.pelota.velocidad = Coordenada(1, 0)

    fisica.aplicar_friccion_pelota(1.0)

    assert estado.pelota.velocidad.x == 0
    assert estado.pelota.velocidad.y == 0


def test_rebote_borde_superior():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    estado.pelota.posicion = Coordenada(50, 60)
    estado.pelota.velocidad = Coordenada(2, 3)

    fisica.bordes_pelota()

    assert estado.pelota.posicion.y == 60
    assert estado.pelota.velocidad.y == -3


def test_rebote_borde_inferior():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    estado.pelota.posicion = Coordenada(50, 0)
    estado.pelota.velocidad = Coordenada(2, -3)

    fisica.bordes_pelota()

    assert estado.pelota.posicion.y == 0
    assert estado.pelota.velocidad.y == 3


def test_rebote_borde_izquierdo():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    estado.pelota.posicion = Coordenada(0, 40)
    estado.pelota.velocidad = Coordenada(-3, 0)

    fisica.bordes_pelota()

    assert estado.pelota.posicion.x == 0
    assert estado.pelota.velocidad.x == 3


def test_rebote_borde_derecho():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    estado.pelota.posicion = Coordenada(100, 40)
    estado.pelota.velocidad = Coordenada(3, 0)

    fisica.bordes_pelota()

    assert estado.pelota.posicion.x == 100
    assert estado.pelota.velocidad.x == -3


def test_colision_jugadores():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    jugador_a = estado.jugadores[(1, 1)]
    jugador_b = estado.jugadores[(2, 2)]

    jugador_a.posicion = Coordenada(10, 30)
    jugador_b.posicion = Coordenada(10.5, 30)

    fisica.resolver_colisiones_jugadores()

    distancia = calcular_distancia(jugador_a.posicion, jugador_b.posicion)

    assert distancia == pytest.approx(1.0)


def test_colision_jugador_pelota():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    jugador = estado.jugadores[(1, 1)]

    jugador.posicion = Coordenada(10, 30)
    estado.pelota.posicion = Coordenada(10.5, 30)
    estado.pelota.velocidad = Coordenada(0, 0)

    fisica.resolver_colisiones_pelota()

    assert estado.pelota.posicion.x == 10.7
    assert estado.pelota.posicion.y == 30
    assert estado.pelota.velocidad.x == 1.0
    assert estado.pelota.velocidad.y == 0


def test_colision_pelota_no_modifica_pateo_reciente():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    jugador = estado.jugadores[(1, 1)]

    jugador.posicion = Coordenada(10, 30)
    estado.pelota.posicion = Coordenada(10.5, 30)
    estado.pelota.velocidad = Coordenada(5, 0)

    estado.tiempo = 10
    jugador.ultimo_pateo = 9.97

    fisica.resolver_colisiones_pelota()

    assert estado.pelota.velocidad.x == 5
    assert estado.pelota.velocidad.y == 0


def test_gol_en_arco_izquierdo():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    estado.pelota.posicion = Coordenada(0, 30)

    fisica.bordes_pelota()

    assert estado.goles_derecho == 1
    assert estado.goles_izquierdo == 0


def test_gol_en_arco_derecho():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    estado.pelota.posicion = Coordenada(100, 30)

    fisica.bordes_pelota()

    assert estado.goles_izquierdo == 1
    assert estado.goles_derecho == 0


def test_reinicio_despues_de_gol():
    estado = crear_estado()
    fisica = FisicaPartido(estado)

    jugador = estado.jugadores[(1, 1)]

    jugador.posicion = Coordenada(50, 40)
    jugador.destino = Coordenada(80, 40)
    jugador.ultimo_pateo = 20

    estado.pelota.posicion = Coordenada(90, 20)
    estado.pelota.velocidad = Coordenada(5, 2)

    fisica.reiniciar_posiciones()

    assert jugador.posicion.x == 10
    assert jugador.posicion.y == 30
    assert jugador.destino is None
    assert jugador.ultimo_pateo == -10

    assert estado.pelota.posicion.x == 50
    assert estado.pelota.posicion.y == 30
    assert estado.pelota.velocidad.x == 0
    assert estado.pelota.velocidad.y == 0







