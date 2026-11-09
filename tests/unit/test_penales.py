import asyncio
from unittest.mock import AsyncMock, Mock
import pytest

from app.partido.estados import Arco, Cancha, Coordenada, EstadoPartido, JugadorEstado, PelotaEstado
from app.partido.motor import MotorPartido
from app.partido.ejecutor import EjecutorPartido
from app.partido.ejecutorliga import EjecutorLiga
from app.capa_2_logica.errores import NoSePuedeElegirComoArquero, SoloPuedenPatearLosTitulares


def ejecutar(coroutine):
    return asyncio.run(coroutine)

def crear_motor_y_ejecutores(codigo_izq="def c(p): pass", codigo_der="def c(p): pass"):
    cancha = Cancha(
        ancho=100, alto=60,
        arco_izquierdo=Arco(poste_superior=Coordenada(0, 40), poste_inferior=Coordenada(0, 20)),
        arco_derecho=Arco(poste_superior=Coordenada(100, 40), poste_inferior=Coordenada(100, 20))
    )
    jugadores = {}
    comportamientos = {}

    for id_j in (1, 2, 3):
        jugadores[(1, id_j)] = JugadorEstado(
            id_jugador=id_j, 
            id_equipo=10, 
            id_usuario=1, 
            nombre=f"J{id_j}", 
            posicion=Coordenada(20, 15),
            control=60, 
            agilidad=60, 
            fuerza=860, 
            poder=60, 
            velocidad=60
        )
        comportamientos[(1, id_j)] = codigo_izq


    for id_j in (4, 5, 6):
        jugadores[(2, id_j)] = JugadorEstado(
            id_jugador=id_j, 
            id_equipo=20, 
            id_usuario=2, 
            nombre=f"J{id_j}", 
            posicion=Coordenada(80, 15),
            control=60, 
            agilidad=60,
            fuerza=60, 
            poder=60, 
            velocidad=60
        )
        comportamientos[(2, id_j)] = codigo_der

    estado = EstadoPartido(
        id_usuario_izquierdo=1, id_usuario_derecho=2, 
        id_equipo_izquierdo=10, id_equipo_derecho=20,
        cancha=cancha, jugadores=jugadores, suplentes={}, comportamientos=comportamientos,
        pelota=PelotaEstado(posicion=Coordenada(50, 30), velocidad=Coordenada(0, 0)),
        codigo_dt={1: "", 2: ""}, dt_activo={1: False, 2: False}, equipos_que_cambiaron=set()
    )
    motor = MotorPartido(estado)
    admin_mock = Mock()
    admin_mock.emitir_partido = AsyncMock()
    
    ejecutor_partido = EjecutorPartido(partido_id=1, motor=motor, duracion=1, admin=admin_mock)
    ejecutor_liga = EjecutorLiga(liga_id=10, partido_id=1, motor=motor, duracion=1, ejecutor_partido=ejecutor_partido, penales=True)
    ejecutor_liga.titulares_finales = dict(motor.estado.jugadores)
    return motor, ejecutor_liga

def test_penal_se_corta_al_hacer_gol_y_suma_al_pateador(monkeypatch):
    codigo_pateador = """
def comportamiento(primitivas):
    if primitivas.pelotaCerca():
        primitivas.patear(primitivas.direccionArcoRival())
    else:
        primitivas.correr(primitivas.direccionPelota())
"""

    codigo_quieto = "def comportamiento(primitivas):\n    pass"
    motor, ejecutor_liga = crear_motor_y_ejecutores(codigo_izq=codigo_quieto, codigo_der=codigo_pateador)

    # simulo que esta la pelota casi en la linea y el jugador ahi atras
    motor.estado.pelota.posicion = Coordenada(8.0, 30.0)
    pateador = motor.estado.jugadores[(2, 4)]
    pateador.posicion = Coordenada(99, 30.0)

    monkeypatch.setattr("app.partido.ejecutorliga.asyncio.sleep", AsyncMock())
    monkeypatch.setattr("app.partido.ejecutorliga.admin_conexiones.emitir_partido", AsyncMock())

    fue_gol = ejecutar(
        ejecutor_liga.ejecutar_un_penal(
            lado_pateador="derecho",
            id_usuario_pateador=2,
            id_jugador_pateador=4,
            comportamiento_pateador=codigo_pateador,
            id_usuario_arquero=1,
            id_jugador_arquero=1,
            comportamiento_arquero=codigo_quieto
        )
    )

    assert fue_gol is False
    assert ejecutor_liga.penales_izquierdo == 0
    assert motor.fisica.en_penales is False
    assert len(motor.estado.jugadores) == 2

def test_pelota_en_arco_propio_durante_penal_no_suma_gol_y_queda_atrapada():
    motor, _ = crear_motor_y_ejecutores()
    estado = motor.estado
    motor.fisica.en_penales = True
    motor.fisica.lado_pateador_penal = "derecho" 

    # si la pelota entra en su propio arco (arco derecho x=100, y=30)
    estado.pelota.posicion = Coordenada(100, 30)
    estado.pelota.velocidad = Coordenada(10, 0)
    motor.fisica.bordes_pelota()

    assert motor.fisica.hubo_gol_penal is False
    assert estado.pelota.posicion.x == 100
    assert estado.pelota.velocidad == Coordenada(0, 0)

def test_configurar_penales_valida_arquero_y_pateadores_titulares():
    motor, ejecutor_liga = crear_motor_y_ejecutores()

    with pytest.raises(NoSePuedeElegirComoArquero):
        ejecutor_liga.configurar_penales_usuario(
            usuario_id=1,
            id_arquero=99,
            comportamiento_arquero="def comportamiento(primitivas):\n    pass",
            comportamiento_pateadores=[(1, "c"), (2, "c"), (3, "c")],
            estado=motor.estado
        )

    with pytest.raises(SoloPuedenPatearLosTitulares):
        ejecutor_liga.configurar_penales_usuario(
            usuario_id=1,
            id_arquero=1,
            comportamiento_arquero="def comportamiento(primitivas):\n    pass",
            comportamiento_pateadores=[(1, "c"), (2, "c"), (99, "c")],
            estado=motor.estado
        )