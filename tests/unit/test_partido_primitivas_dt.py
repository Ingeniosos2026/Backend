import pytest

from app.partido.estados import *
from app.partido.primitivas_dt import PrimitivasDT
from app.partido.comportamientos import comportamiento_atacar, comportamiento_defender, comportamiento_pasar_compañero


def crear_estado_partido():
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
        nombre="Lean",
        posicion=Coordenada(49, 25),
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60)

    jugador_2 = JugadorEstado(
        id_jugador=2,
        id_equipo=10,
        id_usuario=1,
        nombre="Lean2",
        posicion=Coordenada(30, 25),
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60)

    jugador_3 = JugadorEstado(
        id_jugador=3,
        id_equipo=20,
        id_usuario=2,
        nombre="Lean3",
        posicion=Coordenada(80, 25),
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60)

    suplente_1 = JugadorEstado(
        id_jugador=4,
        id_equipo=10,
        id_usuario=1,
        nombre="Suplente1",
        posicion=Coordenada(10, 10),
        control=40,
        agilidad=50,
        fuerza=60,
        poder=70,
        velocidad=80)

    suplente_2 = JugadorEstado(
        id_jugador=5,
        id_equipo=20,
        id_usuario=2,
        nombre="Suplente2",
        posicion=Coordenada(90, 10),
        control=50,
        agilidad=60,
        fuerza=70,
        poder=80,
        velocidad=90)

    pelota = PelotaEstado(
        posicion=Coordenada(50, 25),
        velocidad=Coordenada(0, 0))

    return EstadoPartido(
        id_usuario_izquierdo=1,
        id_usuario_derecho=2,
        id_equipo_izquierdo=10,
        id_equipo_derecho=20,
        cancha=cancha,
        jugadores={
            (1, 1): jugador_1,
            (1, 2): jugador_2,
            (2, 3): jugador_3},
        suplentes={
            (1, 4): suplente_1,
            (2, 5): suplente_2},
        comportamientos={
            (1, 1): comportamiento_pasar_compañero,
            (1, 2): comportamiento_pasar_compañero,
            (1, 4): comportamiento_pasar_compañero,
            (2, 3): comportamiento_atacar},
        codigo_dt={},
        equipos_que_cambiaron=set(),
        dt_activo={1: False, 2: False},
        pelota=pelota)


def crear_posiciones_iniciales():
    return {(1, 1): Coordenada(49, 25),
        (1, 2): Coordenada(30, 25),
        (1, 4): Coordenada(10, 10),
        (2, 3): Coordenada(80, 25),
        (2, 5): Coordenada(90, 10)}

def test_cambiar_comportamiento_ataque():
    estado = crear_estado_partido()

    primitivas = PrimitivasDT(estado=estado, id_usuario=1, posiciones_iniciales=crear_posiciones_iniciales(), eventos=[])
    primitivas.cambiar_comportamiento_ataque()

    assert estado.comportamientos[(1, 1)] == comportamiento_atacar
    assert estado.comportamientos[(1, 2)] == comportamiento_atacar

    assert estado.comportamientos[(2, 3)] == comportamiento_atacar
    assert estado.comportamientos[(1, 4)] == comportamiento_pasar_compañero


def test_cambiar_comportamiento_defensa():
    estado = crear_estado_partido()

    primitivas = PrimitivasDT(estado=estado,id_usuario=1, posiciones_iniciales=crear_posiciones_iniciales(), eventos=[])

    primitivas.cambiar_comportamiento_defensa()

    assert estado.comportamientos[(1, 1)] == comportamiento_defender
    assert estado.comportamientos[(1, 2)] == comportamiento_defender

    assert estado.comportamientos[(2, 3)] == comportamiento_atacar
    assert estado.comportamientos[(1, 4)] == comportamiento_pasar_compañero



def test_cambiar_jugador(monkeypatch):
    estado = crear_estado_partido()
    estado.en_pausa = True
    estado.pausas_realizadas = 1

    posiciones_iniciales = crear_posiciones_iniciales()
    eventos = []

    primitivas = PrimitivasDT(estado=estado,id_usuario=1,posiciones_iniciales=posiciones_iniciales, eventos=eventos)

    monkeypatch.setattr("app.partido.primitivas_dt.random.choice", lambda elementos: (1,1) if (1,1) in elementos else (1, 4))

    posicion_original = estado.jugadores[(1, 1)].posicion
    primitivas.cambiar_jugador()

    # el jugador 1 salio del partido
    assert (1, 1) not in estado.jugadores

    # el suplente 4 ingreso al partido.
    assert (1, 4) in estado.jugadores

    # el jugador que salio ahora es suplente
    assert (1, 1) in estado.suplentes

    # el suplente toma la posicion del jugador que salio
    assert estado.jugadores[(1, 4)].posicion == posicion_original

    # se registro el cambio
    assert (1, 10) in estado.equipos_que_cambiaron

    # se genera el evento
    assert len(eventos) == 1
    assert eventos[0]["accion"] == "cambio_jugador_realizado"

    payload = eventos[0]["payload"]

    assert payload["id_equipo"] == 10
    assert payload["id_usuario"] == 1
    assert payload["jugador_sale_id"] == 1
    assert payload["nombre_jugador_sale"] == "Lean"
    assert payload["jugador_entra_id"] == 4
    assert payload["nombre_jugador_entra"] == "Suplente1"

def test_voy_perdiendo():
    estado = crear_estado_partido()
    estado.goles_izquierdo = 1
    estado.goles_derecho = 2

    primitivas = PrimitivasDT(estado=estado, id_usuario=1, posiciones_iniciales=crear_posiciones_iniciales(), eventos=[])

    assert primitivas.voy_perdiendo() is True
    assert primitivas.voy_ganando() is False
    assert primitivas.esta_empatado() is False

def test_esta_empatado():
    estado = crear_estado_partido()
    estado.goles_izquierdo = 2
    estado.goles_derecho = 2

    primitivas = PrimitivasDT(estado=estado, id_usuario=1, posiciones_iniciales=crear_posiciones_iniciales(), eventos=[])

    assert primitivas.esta_empatado() is True
    assert primitivas.voy_ganando() is False
    assert primitivas.voy_perdiendo() is False

def test_voy_perdiendo_usuario_derecho():
    estado = crear_estado_partido()
    estado.goles_izquierdo = 3
    estado.goles_derecho = 1

    primitivas = PrimitivasDT(estado=estado, id_usuario=2, posiciones_iniciales=crear_posiciones_iniciales(), eventos=[])

    assert primitivas.voy_perdiendo() is True

def test_es_pausa():
    estado = crear_estado_partido()
    estado.en_pausa = True

    primitivas = PrimitivasDT(estado=estado, id_usuario=1, posiciones_iniciales=crear_posiciones_iniciales(), eventos=[])

    assert primitivas.es_pausa() is True