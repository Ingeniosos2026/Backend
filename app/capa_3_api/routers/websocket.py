from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.capa_3_api.websockets.admin_conexiones import admin_conexiones

ws_router = APIRouter()

@ws_router.websocket("/ws/amistoso/{partido_id}")
async def websocket_amistoso(websocket: WebSocket, partido_id: int):
    await admin_conexiones.conectar_lobby(websocket, partido_id)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        admin_conexiones.desconectar_lobby(websocket, partido_id)

@ws_router.websocket("/ws/partido/{partido_id}")
async def websocket_endpoint(websocket: WebSocket, partido_id: int):
    await admin_conexiones.conectar(websocket, partido_id) 
    try:
        while True: # mantiene la conexion abierta 
            data = await websocket.receive_text()
    except WebSocketDisconnect: 
        admin_conexiones.desconectar(websocket, partido_id)

@ws_router.websocket("/ws/notificaciones/{usuario_id}")
async def websocket_notificaciones(websocket: WebSocket, usuario_id: int):
    await admin_conexiones.conectar_global(websocket, usuario_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        admin_conexiones.desconectar_global(usuario_id)