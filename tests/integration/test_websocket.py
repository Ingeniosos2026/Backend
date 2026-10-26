import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.liga_modelos import Liga
from app.capa_0_definicion_bd.models.partidos_modelos import (EstadoPartido, Formacion, Partido, TipoPartido)
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario


def test_conexion_multiple_websockets():
    client = TestClient(app)
    partido_prueba_id = 1913

    # simulo dos personas al mismo partido
    with client.websocket_connect(f"/ws/partido/{partido_prueba_id}") as ws1, \
         client.websocket_connect(f"/ws/partido/{partido_prueba_id}") as ws2:
        
        assert partido_prueba_id in admin_conexiones.conexiones_activas
        assert len(admin_conexiones.conexiones_activas[partido_prueba_id]) == 2

    assert partido_prueba_id not in admin_conexiones.conexiones_activas


def test_emitir_evento_a_todos_los_websockets_del_lobby():
    client = TestClient(app)
    partido_id = 1913

    with client.websocket_connect(f"/ws/amistoso/{partido_id}") as ws1, client.websocket_connect(
        f"/ws/amistoso/{partido_id}"
    ) as ws2:
        asyncio.run(
            admin_conexiones.emitir_lobby(
                partido_id,
                "usuario_unido",
                {"usuario_id": 2},
            )
        )

        mensaje1 = ws1.receive_json()
        mensaje2 = ws2.receive_json()

        esperado = {
            "action": "usuario_unido",
            "payload": {"usuario_id": 2},
        }

        assert mensaje1 == esperado
        assert mensaje2 == esperado


def test_cerrar_lobby_cierra_todas_las_conexiones():
    client = TestClient(app)
    partido_id = 1913

    with client.websocket_connect(f"/ws/amistoso/{partido_id}") as ws1, client.websocket_connect(
        f"/ws/amistoso/{partido_id}"
    ) as ws2:
        assert partido_id in admin_conexiones.conexiones_lobby
        assert len(admin_conexiones.conexiones_lobby[partido_id]) == 2

        asyncio.run(admin_conexiones.cerrar_lobby(partido_id))

        assert partido_id not in admin_conexiones.conexiones_lobby


def test_desconectar_un_usuario_no_elimina_el_lobby():
    client = TestClient(app)
    partido_id = 1913

    with client.websocket_connect(f"/ws/amistoso/{partido_id}") as ws1:
        with client.websocket_connect(f"/ws/amistoso/{partido_id}") as ws2:
            assert len(admin_conexiones.conexiones_lobby[partido_id]) == 2

        assert partido_id in admin_conexiones.conexiones_lobby
        assert len(admin_conexiones.conexiones_lobby[partido_id]) == 1


def test_lobby_se_elimina_al_desconectarse_todos():
    client = TestClient(app)
    partido_id = 1913

    with client.websocket_connect(f"/ws/amistoso/{partido_id}"):
        assert partido_id in admin_conexiones.conexiones_lobby

    assert partido_id not in admin_conexiones.conexiones_lobby


def test_lobby_liga_acepta_varios_usuarios_y_aisla_ids_de_amistosos():
    client = TestClient(app)
    liga_id = 1913

    with client.websocket_connect(f"/ws/liga/{liga_id}") as ws1, client.websocket_connect(
        f"/ws/liga/{liga_id}"
    ) as ws2, client.websocket_connect(f"/ws/amistoso/{liga_id}"):
        clave_liga = ("liga", liga_id)
        assert len(admin_conexiones.conexiones_lobby[clave_liga]) == 2
        assert len(admin_conexiones.conexiones_lobby[liga_id]) == 1

        asyncio.run(
            admin_conexiones.emitir_lobby_liga(
                liga_id,
                "usuario_unido",
                {"usuario_id": 2},
            )
        )

        mensaje_esperado = {
            "action": "usuario_unido",
            "payload": {"usuario_id": 2},
        }
        assert ws1.receive_json() == mensaje_esperado
        assert ws2.receive_json() == mensaje_esperado

    assert ("liga", liga_id) not in admin_conexiones.conexiones_lobby
    assert liga_id not in admin_conexiones.conexiones_lobby


def test_websocket_liga_envia_participantes_actuales_al_conectar(client, db_test):
    owner = Usuario(
        email="Pepito@gmail.com",
        nombre="Pepito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="Boca")
    participantes = [Usuario(
            email=f"participante{indice}@gmail.com",
            nombre=f"Participante {indice}",
            id_avatar=indice,
            contraseña="asd321",
            nombre_club=f"Club {indice}")
        for indice in (1, 2)]
    db_test.add_all([owner, *participantes])
    db_test.commit()
    liga = Liga(
        id_usuario=owner.id_usuario,
        nombre="premier league",
        min_jugadores=3,
        max_jugadores=10,
        duracion_partido=10,
        participantes=participantes)
    db_test.add(liga)
    db_test.commit()

    with client.websocket_connect(f"/ws/liga/{liga.id}") as websocket:
        mensajes = [websocket.receive_json() for _ in range(3)]

    assert {
        mensaje["payload"]["usuario_unido"]["id"]: mensaje
        for mensaje in mensajes } == {
        usuario.id_usuario: {
            "action": "usuario_unido_liga",
            "payload": {
                "usuario_unido": {
                    "id": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "club": usuario.nombre_club}
            }}
        for usuario in [owner, *participantes]
    }


def test_websocket_liga_reenvia_participantes_al_reconectar(client, db_test):
    owner = Usuario(
        email="pepito@gmail.com",
        nombre="Pepito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="Boca")
    participante = Usuario(
        email="tomas@gmail.com",
        nombre="tomas",
        id_avatar=2,
        contraseña="ads321",
        nombre_club="Talleres")
    db_test.add_all([owner, participante])
    db_test.commit()
    liga = Liga(
        id_usuario=owner.id_usuario,
        nombre="superliga",
        min_jugadores=3,
        max_jugadores=10,
        duracion_partido=10,
        participantes=[participante])
    db_test.add(liga)
    db_test.commit()

    esperados = [{
            "action": "usuario_unido_liga",
            "payload": {
                "usuario_unido": {
                    "id": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "club": usuario.nombre_club}}}
        for usuario in [owner, participante]
    ]

    for _ in range(2):
        with client.websocket_connect(f"/ws/liga/{liga.id}") as websocket:
            assert [websocket.receive_json() for _ in range(2)] == esperados


@pytest.mark.parametrize("dos_participantes", [False, True])
def test_websocket_amistoso_envia_estado_actual_al_conectar_y_reconectar(client, db_test, dos_participantes):
    owner = Usuario(
        email="Pepito@gmail.com",
        nombre="Pepito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="Boca")
    participantes = [owner]
    db_test.add(owner)
    db_test.commit()
    equipo_owner = Equipo(id_usuario=owner.id_usuario)
    db_test.add(equipo_owner)

    if dos_participantes:
        participante = Usuario(
            email="tomas@gmail.com",
            nombre="tomas",
            id_avatar=2,
            contraseña="asd321",
            nombre_club="Talleres",
        )
        participantes.append(participante)
        db_test.add(participante)
        db_test.commit()
        equipo_participante = Equipo(id_usuario=participante.id_usuario)
        db_test.add(equipo_participante)
        db_test.commit()
    else:
        equipo_participante = None

    db_test.commit()
    partido = Partido(
        id_usuario_1=owner.id_usuario,
        id_usuario_2=participantes[1].id_usuario if dos_participantes else None,
        id_equipo_1=equipo_owner.id_equipo,
        id_equipo_2=equipo_participante.id_equipo if equipo_participante else None,
        duracion_partido=10,
        formacion_1=Formacion.OFENSIVA,
        formacion_2=Formacion.DEFENSIVA if dos_participantes else None,
        tipo_partido=TipoPartido.AMISTOSO,
        estado_partido=(EstadoPartido.PENDIENTE if dos_participantes else EstadoPartido.DISPONIBLE))
    db_test.add(partido)
    db_test.commit()

    esperado = {
        "action": "estado_inicial_lobby",
        "payload": {
            "competidores": [{
                    "id": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "club": usuario.nombre_club}
                for usuario in participantes
            ]}}

    for _ in range(2):
        with client.websocket_connect(f"/ws/amistoso/{partido.id_partido}") as websocket:
            assert websocket.receive_json() == esperado