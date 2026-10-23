from fastapi import WebSocket
from typing import Dict, List, Tuple, Union

ClaveLobby = Union[int, Tuple[str, int]]            # esto fue necesario para que amistoso y liga no se pisen las conexiones

class AdministradorConexiones:
    def __init__(self):
        
        # mantiene las conexiones activas por usuario_id (usuarios conectados)
        self.conexiones_globales: Dict[int, WebSocket] = {}
          
        # mantiene las conexiones activas por partido_id (usuarios conectados a un partido)
        self.conexiones_activas: Dict[int, List[WebSocket]] = {}

        # conexiones para lobby de amistosos
        self.conexiones_lobby: Dict[ClaveLobby, List[WebSocket]] = {}

    # lobby de amistosos
    async def conectar_lobby(self, websocket: WebSocket, partido_id: int):
        await self._conectar_a_lobby(websocket, partido_id, self.conexiones_lobby)

    async def conectar_lobby_liga(self, websocket: WebSocket, liga_id: int):
        await self._conectar_a_lobby(websocket, ("liga", liga_id), self.conexiones_lobby)

    async def _conectar_a_lobby(
        self,
        websocket: WebSocket,
        lobby_id: ClaveLobby,
        conexiones: Dict[ClaveLobby, List[WebSocket]],
    ):
        await websocket.accept()

        if lobby_id not in conexiones:
            conexiones[lobby_id] = []

        conexiones[lobby_id].append(websocket)

    def desconectar_lobby(self, websocket: WebSocket, partido_id: int):
        self._desconectar_de_lobby(websocket, partido_id, self.conexiones_lobby)

    def desconectar_lobby_liga(self, websocket: WebSocket, liga_id: int):
        self._desconectar_de_lobby(websocket, ("liga", liga_id), self.conexiones_lobby)

    def _desconectar_de_lobby(
        self,
        websocket: WebSocket,
        lobby_id: ClaveLobby,
        conexiones: Dict[ClaveLobby, List[WebSocket]],
    ):
        if lobby_id in conexiones:
            try:
                conexiones[lobby_id].remove(websocket)
            except ValueError:
                pass

            if not conexiones[lobby_id]:
                del conexiones[lobby_id]

    async def emitir_lobby(self, partido_id: int, accion: str, payload: dict):
        await self._emitir_en_lobby(partido_id, accion, payload, self.conexiones_lobby)

    async def emitir_lobby_liga(self, liga_id: int, accion: str, payload: dict):
        await self._emitir_en_lobby(("liga", liga_id), accion, payload, self.conexiones_lobby)

    async def _emitir_en_lobby(
        self,
        lobby_id: ClaveLobby,
        accion: str,
        payload: dict,
        conexiones: Dict[ClaveLobby, List[WebSocket]],
    ):
        if lobby_id not in conexiones:
            return

        mensaje = {"action": accion, "payload": payload}

        for conexion in list(conexiones[lobby_id]):
            try:
                await conexion.send_json(mensaje)
            except RuntimeError:
                self._desconectar_de_lobby(conexion, lobby_id, conexiones)

    async def cerrar_lobby(self, partido_id: int):
        await self._cerrar_lobby(partido_id, self.conexiones_lobby)

    async def cerrar_lobby_liga(self, liga_id: int):
        await self._cerrar_lobby(("liga", liga_id), self.conexiones_lobby)

    async def _cerrar_lobby(
        self,
        lobby_id: ClaveLobby,
        conexiones: Dict[ClaveLobby, List[WebSocket]],
    ):
        if lobby_id not in conexiones:
            return

        for conexion in list(conexiones[lobby_id]):
            try:
                await conexion.close()
            except RuntimeError:
                pass

        conexiones.pop(lobby_id, None)
    
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
    
    # de preferencia esta pero no estoy seguro si usaron la de arriba 
    async def emitir_partido(self, partido_id: int, accion: str, payload: dict):
        if partido_id not in self.conexiones_activas:
            return

        mensaje = {"action": accion, "payload": payload}

        for conexion in list(self.conexiones_activas[partido_id]):
            try:
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