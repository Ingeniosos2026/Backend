import asyncio

from .motor import MotorPartido, T
from .convertidor import estado_a_dict, estados_jugadores_a_dict, eventos_a_dict
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones


class EjecutorPartido:

    def __init__(self, partido_id: int, motor: MotorPartido, duracion: float):
        self.partido_id = partido_id
        self.motor = motor
        self.duracion = duracion

    async def ejecutar(self):

        # avisamos que el partido comenzo
        await admin_conexiones.emitir_partido(partido_id=self.partido_id, accion="partido_iniciado", payload={"tiempo": 0})

        # mandamos el estado inicial antes del primer tick
        await admin_conexiones.emitir_partido(partido_id=self.partido_id, accion="estado_partido", payload={**estado_a_dict(self.motor.estado), "estados_jugadores": [], "acciones": []})

        while self.motor.estado.tiempo < self.duracion:

            estado, estados_jugadores, eventos = self.motor.tick()

            # envio el nuevo estado al front
            await admin_conexiones.emitir_partido(
                partido_id=self.partido_id,
                accion="estado_partido",
                payload={** estado_a_dict(estado), "estados_jugadores": estados_jugadores_a_dict(estados_jugadores, estado), "acciones": eventos_a_dict(eventos)})

            # esperamos hasta el proximo tick, esto es para que no se ejecuten instantaneamente varios ticks
            if self.motor.estado.tiempo < self.duracion:
                await asyncio.sleep(T)

        # avisamos que el partido termino
        await admin_conexiones.emitir_partido(
            partido_id=self.partido_id,
            accion="partido_terminado",
            payload={
                "tiempo": self.motor.estado.tiempo,
                "goles": {"izquierdo": self.motor.estado.goles_izquierdo,
                          "derecho": self.motor.estado.goles_derecho}})