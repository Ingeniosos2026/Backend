import pytest
from app.partido.estados import *
from app.partido.primitivas import Primitivas


def crear_estado_partido():
    cancha = Cancha(
        ancho=100,
        alto=50,
        arco_izquierdo=Arco(poste_superior=Coordenada(0, 20), poste_inferior=Coordenada(0, 30)),
        arco_derecho=Arco(poste_superior=Coordenada(100, 20), poste_inferior=Coordenada(100, 30)))

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
        id_equipo=10,
        id_usuario=1,
        posicion=Coordenada(30, 25),
        control=60,
        agilidad=50,
        fuerza=80,
        poder=70,
        velocidad=50)

    jugador_3 = JugadorEstado(
        id_jugador=3,
        id_equipo=20,
        id_usuario=2,
        posicion=Coordenada(80, 25),
        control=70,
        agilidad=40,
        fuerza=60,
        poder=90,
        velocidad=60)

    pelota = PelotaEstado(posicion=Coordenada(50, 25), velocidad=Coordenada(0, 0))

    return EstadoPartido(
        id_usuario_izquierdo=1,
        id_usuario_derecho=2,
        id_equipo_izquierdo=10,
        id_equipo_derecho=20,
        cancha=cancha,
        jugadores={(1, 1): jugador_1, (1, 2): jugador_2, (2, 3): jugador_3},
        comportamientos={},
        pelota=pelota)


def test_correr():
    estado = crear_estado_partido()

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    destino = Coordenada(50, 30)

    primitivas.correr(destino)

    jugador = estado.jugadores[(1, 1)]

    assert jugador.destino == destino


def test_correr_destino_fuera_de_cancha():
    estado = crear_estado_partido()

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    destino = Coordenada(101, 30)

    with pytest.raises(ValueError, match="El destino esta fuera de la cancha"):
        primitivas.correr(destino)


def test_patear():
    estado = crear_estado_partido()
    eventos = []
    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=eventos)

    direccion = Coordenada(100, 25)

    resultado = primitivas.patear(direccion)

    assert resultado is True
    assert estado.pelota.velocidad.x > 0
    assert estado.pelota.velocidad.y == pytest.approx(0)
    assert estado.jugadores[(1, 1)].ultimo_pateo == estado.tiempo

    assert eventos[0].id_jugador == 1
    assert eventos[0].id_usuario == 1   
    assert eventos[0].accion == "pateando"


def test_patear_pelota_fuera_de_alcance():
    estado = crear_estado_partido()

    estado.pelota.posicion = Coordenada(55, 25)

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    direccion = Coordenada(100, 25)

    resultado = primitivas.patear(direccion)

    assert resultado is False
    assert estado.pelota.velocidad == Coordenada(0, 0)


def test_patear_direccion_invalida():
    estado = crear_estado_partido()

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    resultado = primitivas.patear(Coordenada(50, 25))

    assert resultado is False


def test_direccion_pelota():
    estado = crear_estado_partido()

    estado.pelota.posicion = Coordenada(40, 30)

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    resultado = primitivas.direccionPelota()

    assert resultado == Coordenada(40, 30)


def test_direccion_compañeros():
    estado = crear_estado_partido()

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    resultado = primitivas.direccionCompañeros()

    assert Coordenada(30, 25) in resultado
    assert len(resultado) == 1


def test_direccion_rivales():
    estado = crear_estado_partido()

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    resultado = primitivas.direccionRivales()

    assert Coordenada(80, 25) in resultado
    assert len(resultado) == 1


def test_pelota_cerca():
    estado = crear_estado_partido()

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    assert primitivas.pelotaCerca() is True


def test_pelota_lejos():
    estado = crear_estado_partido()

    estado.pelota.posicion = Coordenada(60, 25)

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    assert primitivas.pelotaCerca() is False


def test_direccion_arco_rival():
    estado = crear_estado_partido()

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    resultado = primitivas.direccionArcoRival()

    assert resultado == Coordenada(100, 25)


def test_direccion_arco_propio():
    estado = crear_estado_partido()

    primitivas = Primitivas(estado=estado, id_usuario=1, id_jugador=1, eventos=[])

    resultado = primitivas.direccionArcoPropio()

    assert resultado == Coordenada(0, 25)


def test_direccion_arco_rival_usuario_derecho():
    estado = crear_estado_partido()

    primitivas = Primitivas(estado=estado, id_usuario=2, id_jugador=3, eventos=[])

    resultado = primitivas.direccionArcoRival()

    assert resultado == Coordenada(0, 25)


def test_direccion_arco_propio_usuario_derecho():
    estado = crear_estado_partido()

    primitivas = Primitivas(estado=estado, id_usuario=2, id_jugador=3, eventos=[])

    resultado = primitivas.direccionArcoPropio()

    assert resultado == Coordenada(100, 25)
