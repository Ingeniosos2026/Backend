from fastapi import WebSocket
from typing import Dict, List

class AdministradorConexiones:
    def __init__(self):
        self.conexiones_activas: Dict[int, List[WebSocket]] = {}

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

admin_conexiones = AdministradorConexiones()