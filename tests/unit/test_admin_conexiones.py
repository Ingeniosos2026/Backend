import asyncio
from unittest.mock import AsyncMock

from app.capa_3_api.websockets.admin_conexiones import AdministradorConexiones

# helper para los websockets
def ejecutar(coroutine):
    return asyncio.run(coroutine)


def test_conectar_y_desconectar_lobby_registra_y_limpia_conexion():
    admin = AdministradorConexiones()
    websocket = AsyncMock()

    ejecutar(admin.conectar_lobby(websocket, 12))

    websocket.accept.assert_awaited_once()
    assert admin.conexiones_lobby[12] == [websocket]

    admin.desconectar_lobby(websocket, 12)
    admin.desconectar_lobby(websocket, 12)

    assert 12 not in admin.conexiones_lobby
    admin.desconectar_lobby(websocket, 999)
    admin.conexiones_lobby[13] = [AsyncMock()]
    admin.desconectar_lobby(websocket, 13)
    assert len(admin.conexiones_lobby[13]) == 1


def test_emitir_lobby_sin_conexiones_no_hace_nada():
    admin = AdministradorConexiones()

    ejecutar(admin.emitir_lobby(12, "usuario_unido", {"usuario_id": 5}))

    assert admin.conexiones_lobby == {}


def test_emitir_lobby_envia_evento_y_elimina_conexion_con_error():
    admin = AdministradorConexiones()
    websocket_activo = AsyncMock()
    websocket_cerrado = AsyncMock()
    websocket_cerrado.send_json.side_effect = RuntimeError("socket cerrado")
    admin.conexiones_lobby[12] = [websocket_activo, websocket_cerrado]

    ejecutar(admin.emitir_lobby(12, "usuario_unido", {"usuario_id": 5}))

    websocket_activo.send_json.assert_awaited_once_with({
        "action": "usuario_unido",
        "payload": {"usuario_id": 5},
    })
    assert admin.conexiones_lobby[12] == [websocket_activo]


def test_cerrar_lobby_cierra_conexiones_y_es_seguro_si_no_existe():
    admin = AdministradorConexiones()
    websocket = AsyncMock()
    websocket_con_error = AsyncMock()
    websocket_con_error.close.side_effect = RuntimeError("socket cerrado")
    admin.conexiones_lobby[12] = [websocket, websocket_con_error]

    ejecutar(admin.cerrar_lobby(999))
    ejecutar(admin.cerrar_lobby(12))

    websocket.close.assert_awaited_once()
    websocket_con_error.close.assert_awaited_once()
    assert 12 not in admin.conexiones_lobby


def test_conectar_y_desconectar_partido_registra_y_limpia_conexion():
    admin = AdministradorConexiones()
    websocket = AsyncMock()

    ejecutar(admin.conectar(websocket, 12))

    websocket.accept.assert_awaited_once()
    assert admin.conexiones_activas[12] == [websocket]

    admin.desconectar(websocket, 12)
    admin.desconectar(websocket, 999)

    assert 12 not in admin.conexiones_activas
    admin.conexiones_activas[13] = [AsyncMock()]
    admin.desconectar(websocket, 13)
    assert len(admin.conexiones_activas[13]) == 1


def test_emitir_estado_partido_sin_conexiones_no_hace_nada():
    admin = AdministradorConexiones()

    ejecutar(admin.emitir_estado_partido(12, {"estado": "en_curso"}))

    assert admin.conexiones_activas == {}


def test_emitir_estado_partido_difunde_y_limpia_conexion_con_error():
    admin = AdministradorConexiones()
    websocket_activo = AsyncMock()
    websocket_cerrado = AsyncMock()
    websocket_cerrado.send_json.side_effect = RuntimeError("socket cerrado")
    admin.conexiones_activas[12] = [websocket_activo, websocket_cerrado]

    ejecutar(admin.emitir_estado_partido(12, {"estado": "en_curso"}))

    websocket_activo.send_json.assert_awaited_once_with({
        "action": "estado_partido",
        "payload": {"estado": "en_curso"},
    })
    assert admin.conexiones_activas[12] == [websocket_activo]


def test_conectar_y_desconectar_usuario_global():
    admin = AdministradorConexiones()
    websocket = AsyncMock()

    ejecutar(admin.conectar_global(websocket, 7))

    websocket.accept.assert_awaited_once()
    assert admin.conexiones_globales[7] is websocket

    admin.desconectar_global(7)
    admin.desconectar_global(7)

    assert 7 not in admin.conexiones_globales


def test_difundir_envia_a_todos_y_continua_si_un_socket_falla():
    admin = AdministradorConexiones()
    websocket_con_error = AsyncMock()
    websocket_activo = AsyncMock()
    websocket_con_error.send_json.side_effect = RuntimeError("socket cerrado")
    admin.conexiones_globales = {
        1: websocket_con_error,
        2: websocket_activo,
    }

    ejecutar(admin.difundir("partido_actualizado", {"partido_id": 12}))

    websocket_con_error.send_json.assert_awaited_once_with({
        "action": "partido_actualizado",
        "payload": {"partido_id": 12},
    })
    websocket_activo.send_json.assert_awaited_once_with({
        "action": "partido_actualizado",
        "payload": {"partido_id": 12},
    })
