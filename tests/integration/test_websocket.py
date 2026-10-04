import pytest
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