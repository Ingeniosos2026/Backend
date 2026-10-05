from app.capa_0_definicion_bd.models.jugadores_modelos import *
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion
from .estados import *

ANCHO_CANCHA = 100
ALTO_CANCHA = 60
LARGO_ARCO = 20


def crear_cancha() -> Cancha:

    centro_y = ALTO_CANCHA / 2
    mitad_arco = LARGO_ARCO / 2
    arco_izquierdo = Arco(
        poste_superior=Coordenada(x=0, y=centro_y + mitad_arco),
        poste_inferior=Coordenada(x=0,y=centro_y - mitad_arco))

    arco_derecho = Arco(
        poste_superior=Coordenada(x=ANCHO_CANCHA, y=centro_y + mitad_arco),
        poste_inferior=Coordenada(x=ANCHO_CANCHA, y=centro_y - mitad_arco))

    return Cancha(
        ancho=ANCHO_CANCHA,
        alto=ALTO_CANCHA,
        arco_izquierdo=arco_izquierdo,
        arco_derecho=arco_derecho
    )


def obtener_posiciones_formacion(formacion: Formacion, lado: str, cancha: Cancha) -> list[Coordenada]:

    ancho = cancha.ancho
    alto = cancha.alto

    y_abajo = alto / 4
    y_medio = alto / 2
    y_arriba = 3 * alto / 4

    if lado == "izquierdo":
        x_atras = ancho / 8
        x_adelante = 3 * ancho / 8

    else:
        x_atras = 7 * ancho / 8
        x_adelante = 5 * ancho / 8

    if formacion == Formacion.OFENSIVA:
        return [
            Coordenada(x_adelante, y_abajo),
            Coordenada(x_adelante, y_medio),
            Coordenada(x_adelante, y_arriba)]

    if formacion == Formacion.DEFENSIVA:
        return [
            Coordenada(x_atras, y_abajo),
            Coordenada(x_atras, y_medio),
            Coordenada(x_atras, y_arriba)]

    if formacion == Formacion.C:
        return [
            Coordenada(x_adelante, y_abajo),
            Coordenada(x_atras, y_medio),
            Coordenada(x_adelante, y_arriba)]

    if formacion == Formacion.D:
        return [
            Coordenada(x_atras, y_abajo),
            Coordenada(x_adelante, y_medio),
            Coordenada(x_atras, y_arriba)]

    raise ValueError("Formacion no valida")


def crear_jugadores_estado(jugadores: list[Jugador], id_usuario: int, id_equipo: int, posiciones: list[Coordenada]):
    titulares = [jugador for jugador in jugadores if jugador.estado == EstadoJugador.TITULAR]

    if len(titulares) != 3:
        raise ValueError("un equipo debe tener exactamente 3 jugadores titulares")

    resultado_jugadores = {}
    resultado_comportamientos = {}

    # el zip combina elementos de dos iterables agrupandolos en pares dentro de un iterador de tuplas (la primera vez que escuho del zip, muy util parece)
    for jugador, posicion in zip(titulares, posiciones):
        jugador_estado = JugadorEstado(
            id_jugador=jugador.id_jugador,
            id_equipo=id_equipo,
            id_usuario=id_usuario,
            posicion=posicion,
            control=jugador.control,
            agilidad=jugador.agilidad,
            fuerza=jugador.fuerza,
            poder=jugador.poder,
            velocidad=jugador.velocidad
        )

        clave = (id_usuario, jugador.id_jugador)
        resultado_jugadores[clave] = jugador_estado

        if jugador.comportamiento is None:
            raise ValueError("El jugador no tiene un comportamiento asignado")

        resultado_comportamientos[clave] = jugador.comportamiento.codigo

    return resultado_jugadores, resultado_comportamientos


def crear_estado_partido(partido) -> EstadoPartido:


    cancha = crear_cancha()
    if partido.equipo_1 is None:
        raise ValueError("El equipo 1 no existe")

    if partido.equipo_2 is None:
        raise ValueError("El equipo 2 no existe")

    if partido.formacion_1 is None:
        raise ValueError("El equipo 1 no tiene formacion")

    if partido.formacion_2 is None:
        raise ValueError("El equipo 2 no tiene formacion")

    posiciones_1 = obtener_posiciones_formacion(partido.formacion_1, "izquierdo", cancha)

    posiciones_2 = obtener_posiciones_formacion(partido.formacion_2, "derecho", cancha)

    jugadores_1, comportamientos_1 = crear_jugadores_estado(
        jugadores=partido.equipo_1.jugadores_amistosos,
        id_usuario=partido.id_usuario_1,
        id_equipo=partido.id_equipo_1,
        posiciones=posiciones_1)

    jugadores_2, comportamientos_2 = crear_jugadores_estado(
        jugadores=partido.equipo_2.jugadores_amistosos,
        id_usuario=partido.id_usuario_2,
        id_equipo=partido.id_equipo_2,
        posiciones=posiciones_2)

    jugadores = {**jugadores_1, **jugadores_2} # ** sirve para fusionar diccionarios

    comportamientos = {**comportamientos_1, **comportamientos_2}

    pelota = PelotaEstado(posicion=Coordenada(x=cancha.ancho/2, y=cancha.alto/2), velocidad=Coordenada(x=0, y=0))

    return EstadoPartido(
        id_usuario_izquierdo=partido.id_usuario_1,
        id_usuario_derecho=partido.id_usuario_2,
        id_equipo_izquierdo=partido.id_equipo_1,
        id_equipo_derecho=partido.id_equipo_2,
        cancha=cancha,
        jugadores=jugadores,
        comportamientos=comportamientos,
        pelota=pelota)