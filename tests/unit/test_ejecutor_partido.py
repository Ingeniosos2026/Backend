import asyncio
from unittest.mock import AsyncMock, Mock
import pytest

from app.partido.estados import Arco,Cancha, Coordenada, EstadoPartido, JugadorEstado, PelotaEstado
from app.partido.motor import MotorPartido, T
from app.partido.ejecutor import EjecutorPartido, DURACION_PAUSA_ENTRETIEMPO, DURACION_PAUSA_COOLING_BREAK

from app.capa_2_logica.resultados import CambioJugadorResultado
from app.capa_2_logica.errores import NoSePuedeCambiarJugador

# helper para los websockets
def ejecutar(coroutine):
    return asyncio.run(coroutine)

def crear_motor_prueba() -> MotorPartido:
    cancha = Cancha(
        ancho=100,
        alto=50,
        arco_izquierdo=Arco(poste_superior=Coordenada(0, 20), poste_inferior=Coordenada(0, 30)),
        arco_derecho=Arco(poste_superior=Coordenada(100, 20), poste_inferior=Coordenada(100, 30)),
    )
    jugador_1 = JugadorEstado(
        id_jugador=1, id_equipo=10, id_usuario=1, nombre="Lean", posicion=Coordenada(20, 25),
        control=50, agilidad=60, fuerza=70, poder=80, velocidad=40
    )
    jugador_2 = JugadorEstado(
        id_jugador=2, id_equipo=20, id_usuario=2, nombre="Lean2", posicion=Coordenada(80, 25),
        control=60, agilidad=50, fuerza=80, poder=70, velocidad=50
    )
    estado = EstadoPartido(
        id_usuario_izquierdo=1,
        id_usuario_derecho=2,
        id_equipo_izquierdo=10,
        id_equipo_derecho=20,
        cancha=cancha,
        jugadores={(1, 1): jugador_1, (2, 2): jugador_2},
        comportamientos={
            (1, 1): "def comportamiento(primitivas):\n    pass",
            (2, 2): "def comportamiento(primitivas):\n    pass",
        },
        suplentes={},
        codigo_dt={},
        dt_activo={1: False, 2: False},
        pelota=PelotaEstado(posicion=Coordenada(50, 25), velocidad=Coordenada(0, 0)),
    )
    return MotorPartido(estado)

def test_configuracion_inicial_de_pausas():
    motor = crear_motor_prueba()
    ejecutor = EjecutorPartido(partido_id=1, motor=motor, duracion=300)

    assert ejecutor.duracion_pausa_entretiempo == DURACION_PAUSA_ENTRETIEMPO
    assert ejecutor.duracion_pausa_cooling_break == DURACION_PAUSA_COOLING_BREAK
    assert ejecutor.tiempos_pausa == [75.0, 150.0, 225.0]
    assert ejecutor.pausas_realizadas == 0
    assert motor.estado.en_pausa is False

def test_pausar_y_reanudar_emiten_eventos_ws():
    motor = crear_motor_prueba()
    admin_mock = Mock()
    admin_mock.emitir_partido = AsyncMock()

    ejecutor = EjecutorPartido(partido_id=10, motor=motor, duracion=100, duracion_pausa_cooling_break=10, duracion_pausa_entretiempo=20, admin=admin_mock)

    # pausamos el partido
    ejecutar(ejecutor.pausar())
    assert motor.estado.en_pausa is True
    admin_mock.emitir_partido.assert_awaited_once_with(
        partido_id=10,
        accion="partido_pausado",
        payload={"tiempo": 0.0, "numero_pausa": 1, "duracion_pausa": 10.0},
    )

    # reanudamos el partido
    ejecutar(ejecutor.reanudar())
    assert motor.estado.en_pausa is False
    admin_mock.emitir_partido.assert_awaited_with(
        partido_id=10,
        accion="partido_reanudado",
        payload={"tiempo": 0.0},
    )

def test_ejecutor_realiza_exactamente_3_pausas_durante_el_partido(monkeypatch):
    motor = crear_motor_prueba()
    admin_mock = Mock()
    admin_mock.emitir_partido = AsyncMock()

    monkeypatch.setattr("app.partido.ejecutor.SessionLocal", Mock()) 
    monkeypatch.setattr("app.partido.ejecutor.crear_servicio", Mock())
    
    ejecutor = EjecutorPartido(
        partido_id=99,
        motor=motor,
        duracion= 4 * T,
        duracion_pausa_entretiempo= 0,
        duracion_pausa_cooling_break=0,
        admin=admin_mock,
    )

    ejecutar(ejecutor.ejecutar())

    assert ejecutor.pausas_realizadas == 3
    assert motor.estado.en_pausa is False

    acciones_emitidas = [
        llamada.kwargs["accion"]
        for llamada in admin_mock.emitir_partido.await_args_list
    ]

    assert acciones_emitidas.count("partido_pausado") == 3
    assert acciones_emitidas.count("partido_reanudado") == 3
    assert acciones_emitidas[0] == "partido_iniciado"
    assert acciones_emitidas[-1] == "partido_terminado"

def test_puede_realizar_cambio():
    motor = crear_motor_prueba()
    ejecutor = EjecutorPartido(partido_id=10, motor=motor, duracion=100)

    assert ejecutor.puede_realizar_cambio(10) is False

    motor.estado.en_pausa = True

    # no puede cambiar si todavia no hay una pausa
    assert ejecutor.puede_realizar_cambio(10) is False

    ejecutor.pausas_realizadas = 1

    # puede cambiar durante la primera pausa
    assert ejecutor.puede_realizar_cambio(10) is True

    # si ya cambio durante esa pausa, no puede volver a hacerl
    ejecutor.equipos_que_cambiaron.add((1, 10))

    assert ejecutor.puede_realizar_cambio(10) is False

    # otro equipo si puede cambiar durante la misma pausa
    assert ejecutor.puede_realizar_cambio(20) is True

    # no puede cambiar mas de 3 pausas
    ejecutor.pausas_realizadas = 4
    assert ejecutor.puede_realizar_cambio(10) is False

def test_solicitar_cambio_queda_cambio_pendiente():
    motor = crear_motor_prueba()
    ejecutor = EjecutorPartido(partido_id=10, motor=motor, duracion=100)

    resultado = CambioJugadorResultado(
        id_jugador=3,
        nombre="Lean",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60,
        codigo_comportamiento="estoy cansado de tanto test profe")

    ejecutar(ejecutor.solicitar_cambio(
        usuario_id=1,
        jugador_sale_id=1,
        resultado=resultado))

    assert ejecutor.cambios_pendientes == {10: (1, 1, resultado)}
    assert ejecutor.equipos_que_cambiaron == set()

def test_solicitar_otro_cambio_pisa_el_anterior():
    motor = crear_motor_prueba()
    ejecutor = EjecutorPartido(partido_id=10, motor=motor, duracion=100)

    resultado_1 = CambioJugadorResultado(
        id_jugador=3,
        nombre="Lean",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60,
        codigo_comportamiento="estoy cansado de tanto test profe")
    
    resultado_2 = CambioJugadorResultado(
        id_jugador=4,
        nombre="Lean",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60,
        codigo_comportamiento="estoy cansado de tanto test profe")

    ejecutar(ejecutor.solicitar_cambio(
        usuario_id=1,
        jugador_sale_id=1,
        resultado=resultado_1))

    ejecutar(ejecutor.solicitar_cambio(
        usuario_id=1,
        jugador_sale_id=1,
        resultado=resultado_2))

    assert ejecutor.cambios_pendientes == {10: (1, 1, resultado_2)}


def test_no_permitir_mas_de_tres_cambios_por_equipo():
    motor = crear_motor_prueba()
    ejecutor = EjecutorPartido(partido_id=10, motor=motor, duracion=100)

    ejecutor.equipos_que_cambiaron = {(1, 10), (2, 10), (3, 10)}

    resultado = CambioJugadorResultado(
        id_jugador=3,
        nombre="Lean",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60,
        codigo_comportamiento="ingenieria la mejor materia de la facu")

    with pytest.raises(NoSePuedeCambiarJugador):
        ejecutar(ejecutor.solicitar_cambio(usuario_id=1, jugador_sale_id=1, resultado=resultado))

    assert ejecutor.cambios_pendientes == {}


def test_realizar_cambio_correctamente():
    motor = crear_motor_prueba()
    # Agrego al jugador 3 como suplente.
    jugador_entra = JugadorEstado(
        id_jugador=3,
        id_equipo=10,
        id_usuario=1,
        nombre="Lean",
        posicion=Coordenada(x=0, y=0),
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60
    )

    clave_entra = (1, 3)

    motor.estado.suplentes[clave_entra] = jugador_entra
    motor.estado.comportamientos[clave_entra] = "hola"

    
    admin_mock = Mock()
    admin_mock.emitir_partido = AsyncMock()

    ejecutor = EjecutorPartido(
        partido_id=10,
        motor=motor,
        duracion=100,
        admin=admin_mock)

    motor.estado.en_pausa = True
    ejecutor.pausas_realizadas = 1

    resultado = CambioJugadorResultado(
        id_jugador=3,
        nombre="Lean",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60,
        codigo_comportamiento="ingenieria la mejor materia de la facu")

    ejecutar(ejecutor.realizar_cambio(
        usuario_id=1,
        id_equipo=10,
        jugador_sale_id=1,
        resultado=resultado))

    # el jugador que sale ya no esta en el estad
    assert (1, 1) in motor.estado.suplentes
    assert (1, 1) not in motor.estado.jugadores

    # el jugador que entra esta en el estado
    assert (1, 3) in motor.estado.jugadores
    assert (1, 3) not in motor.estado.suplentes

    assert motor.estado.jugadores[(1, 3)].posicion == motor.estado.suplentes[(1, 1)].posicion

    # verifico que se conservam los comportamientos
    assert (1, 1) in motor.estado.comportamientos
    assert (1, 3) in motor.estado.comportamientos

    admin_mock.emitir_partido.assert_awaited_once()

def test_alternar_estado_dt_de_false_a_true():
    motor = crear_motor_prueba()
    ejecutor = EjecutorPartido(partido_id=10, motor=motor, duracion=100)

    assert motor.estado.dt_activo[1] is False

    resultado = ejecutor.alternar_estado_dt(usuario_id=1)

    assert resultado is True
    assert motor.estado.dt_activo[1] is True

    # El estado del otro usuario no se modifica.
    assert motor.estado.dt_activo[2] is False


def test_alternar_estado_dt_de_true_a_false():
    motor = crear_motor_prueba()
    ejecutor = EjecutorPartido(partido_id=10, motor=motor, duracion=100)

    motor.estado.dt_activo[1] = True

    resultado = ejecutor.alternar_estado_dt(usuario_id=1)

    assert resultado is False
    assert motor.estado.dt_activo[1] is False

    # El estado del otro usuario no se modifica.
    assert motor.estado.dt_activo[2] is False