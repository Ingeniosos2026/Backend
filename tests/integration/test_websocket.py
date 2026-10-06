import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones


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