import asyncio
from unittest.mock import AsyncMock, Mock
import pytest

from app.partido.estados import Arco,Cancha, Coordenada, EstadoPartido, JugadorEstado, PelotaEstado
from app.partido.motor import MotorPartido, T
from app.partido.ejecutor import EjecutorPartido, DURACION_PAUSA_ENTRETIEMPO, DURACION_PAUSA_COOLING_BREAK

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
        id_jugador=1, id_equipo=10, id_usuario=1, posicion=Coordenada(20, 25),
        control=50, agilidad=60, fuerza=70, poder=80, velocidad=40
    )
    jugador_2 = JugadorEstado(
        id_jugador=2, id_equipo=20, id_usuario=2, posicion=Coordenada(80, 25),
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
    assert ejecutor.pausado is False

def test_pausar_y_reanudar_emiten_eventos_ws():
    motor = crear_motor_prueba()
    admin_mock = Mock()
    admin_mock.emitir_partido = AsyncMock()

    ejecutor = EjecutorPartido(partido_id=10, motor=motor, duracion=100, duracion_pausa_cooling_break=10, duracion_pausa_entretiempo=20, admin=admin_mock)

    # pausamos el partido
    ejecutar(ejecutor.pausar())
    assert ejecutor.pausado is True
    admin_mock.emitir_partido.assert_awaited_once_with(
        partido_id=10,
        accion="partido_pausado",
        payload={"tiempo": 0.0, "numero_pausa": 0, "duracion_pausa": 10.0},
    )

    # reanudamos el partido
    ejecutar(ejecutor.reanudar())
    assert ejecutor.pausado is False
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
    assert ejecutor.pausado is False

    acciones_emitidas = [
        llamada.kwargs["accion"]
        for llamada in admin_mock.emitir_partido.await_args_list
    ]

    assert acciones_emitidas.count("partido_pausado") == 3
    assert acciones_emitidas.count("partido_reanudado") == 3
    assert acciones_emitidas[0] == "partido_iniciado"
    assert acciones_emitidas[-1] == "partido_terminado"