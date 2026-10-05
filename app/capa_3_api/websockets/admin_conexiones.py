from fastapi import WebSocket
from typing import Dict, List

class AdministradorConexiones:
    def __init__(self):
        
        # mantiene las conexiones activas por usuario_id (usuarios conectados)
        self.conexiones_globales: Dict[int, WebSocket] = {}
          
        # mantiene las conexiones activas por partido_id (usuarios conectados a un partido)
        self.conexiones_activas: Dict[int, List[WebSocket]] = {}

        # conexiones para lobby de amistosos
        self.conexiones_lobby: Dict[int, List[WebSocket]] = {}

    # lobby de amistosos
    async def conectar_lobby(self, websocket: WebSocket, partido_id: int):
        await websocket.accept()

        if partido_id not in self.conexiones_lobby:
            self.conexiones_lobby[partido_id] = []

        self.conexiones_lobby[partido_id].append(websocket)

    def desconectar_lobby(self, websocket: WebSocket, partido_id: int):
        if partido_id in self.conexiones_lobby:
            try:
                self.conexiones_lobby[partido_id].remove(websocket)
            except ValueError:
                pass

            if not self.conexiones_lobby[partido_id]:
                del self.conexiones_lobby[partido_id]

    async def emitir_lobby(self, partido_id: int, accion: str, payload: dict):
        if partido_id not in self.conexiones_lobby:
            return

        mensaje = {"action": accion, "payload": payload}

        for conexion in list(self.conexiones_lobby[partido_id]):
            try:
                await conexion.send_json(mensaje)
            except RuntimeError:
                self.desconectar_lobby(conexion, partido_id)

    async def cerrar_lobby(self, partido_id: int):
        if partido_id not in self.conexiones_lobby:
            return

        for conexion in list(self.conexiones_lobby[partido_id]):
            try:
                await conexion.close()
            except RuntimeError:
                pass

        self.conexiones_lobby.pop(partido_id, None)
    
    # --- METODOS PARA PARTIDOS --- 

    async def conectar(self, websocket: WebSocket, partido_id: int):
        await websocket.accept() 
        if partido_id not in self.conexiones_activas: 
            self.conexiones_activas[partido_id] = [] 
        self.conexiones_activas[partido_id].append(websocket)  

    def desconectar(self, websocket: WebSocket, partido_id: int):
        # Verificar que exitsa el partido_id en el dict 
        if partido_id in self.conexiones_activas: 
            try:
                self.conexiones_activas[partido_id].remove(websocket)
            except ValueError: 
                pass
            
            # en caso que la lista de conexiones quede vacia para este partido, se borra  
            if not self.conexiones_activas[partido_id]:
                del self.conexiones_activas[partido_id]

    async def emitir_estado_partido(self, partido_id: int, estado: dict):
        if partido_id in self.conexiones_activas:
            for conexion in list(self.conexiones_activas[partido_id]):
                try:
                    mensaje = {
                        "action": "estado_partido",
                        "payload": estado
                    }
                    await conexion.send_json(mensaje)
                
                except RuntimeError:
                    self.desconectar(conexion, partido_id)

    # --- METODOS PARA USUARIOS ---

    async def conectar_global (self, websocket: WebSocket, usuario_id: int): 
        await websocket.accept()
        self.conexiones_globales[usuario_id] = websocket

    def desconectar_global(self, usuario_id: int):
        if usuario_id in self.conexiones_globales:
            del self.conexiones_globales[usuario_id] 

    async def difundir (self, accion: str, payload: dict):
        mensaje = { "action": accion, 
                    "payload": payload
        } 

        for conexion in list(self.conexiones_globales.values()):
            try:
                await conexion.send_json(mensaje)
            except RuntimeError:
                pass 

admin_conexiones = AdministradorConexiones()