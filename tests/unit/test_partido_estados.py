from app.partido.estados import *

def test_coordenada():
    coordenada = Coordenada(10, 20)
    assert coordenada.x == 10
    assert coordenada.y == 20

def test_centro_arco():
    arco = Arco(poste_superior=Coordenada(0, 10), poste_inferior=Coordenada(0, 20))

    centro = arco.centro

    assert centro.x == 0
    assert centro.y == 15


def test_cancha():
    arco_izquierdo = Arco(poste_superior=Coordenada(0, 20), poste_inferior=Coordenada(0, 30))

    arco_derecho = Arco(poste_superior=Coordenada(100, 20), poste_inferior=Coordenada(100, 30))

    cancha = Cancha(
        ancho=100,
        alto=50,
        arco_izquierdo=arco_izquierdo,
        arco_derecho=arco_derecho)

    assert cancha.ancho == 100
    assert cancha.alto == 50
    assert cancha.arco_izquierdo == arco_izquierdo
    assert cancha.arco_derecho == arco_derecho

def test_jugador_estado():
    posicion = Coordenada(20, 25)

    jugador = JugadorEstado(
        id_jugador=1,
        id_equipo=10,
        posicion=posicion,
        control=50,
        agilidad=60,
        fuerza=70,
        poder=80,
        velocidad=40)

    assert jugador.id_jugador == 1
    assert jugador.id_equipo == 10
    assert jugador.posicion == posicion
    assert jugador.control == 50
    assert jugador.agilidad == 60
    assert jugador.fuerza == 70
    assert jugador.poder == 80
    assert jugador.velocidad == 40
    assert jugador.destino is None
    assert jugador.ultimo_pateo == -10.0


def test_pelota_estado():
    posicion = Coordenada(50, 25)
    velocidad = Coordenada(10, -5)

    pelota = PelotaEstado(posicion=posicion, velocidad=velocidad)

    assert pelota.posicion == posicion
    assert pelota.velocidad == velocidad


def test_estado_partido():
    cancha = Cancha(
        ancho=100,
        alto=50,
        arco_izquierdo=Arco(poste_superior=Coordenada(0, 20), poste_inferior=Coordenada(0, 30)),
        arco_derecho=Arco(poste_superior=Coordenada(100, 20), poste_inferior=Coordenada(100, 30)))

    jugador_1 = JugadorEstado(
        id_jugador=1,
        id_equipo=10,
        posicion=Coordenada(20, 25),
        control=50,
        agilidad=60,
        fuerza=70,
        poder=80,
        velocidad=40)

    jugador_2 = JugadorEstado(
        id_jugador=2,
        id_equipo=20,
        posicion=Coordenada(80, 25),
        control=60,
        agilidad=50,
        fuerza=80,
        poder=70,
        velocidad=50)

    pelota = PelotaEstado(posicion=Coordenada(50, 25), velocidad=Coordenada(0, 0))

    jugadores = {(1, 1): jugador_1, (2, 2): jugador_2}

    estado = EstadoPartido(
        id_usuario_izquierdo=1,
        id_usuario_derecho=2,
        id_equipo_izquierdo=10,
        id_equipo_derecho=20,
        cancha=cancha,
        jugadores=jugadores,
        pelota=pelota)

    assert estado.id_usuario_izquierdo == 1
    assert estado.id_usuario_derecho == 2

    assert estado.id_equipo_izquierdo == 10
    assert estado.id_equipo_derecho == 20

    assert estado.cancha == cancha
    assert estado.jugadores == jugadores
    assert estado.pelota == pelota
    assert estado.tiempo == 0.0