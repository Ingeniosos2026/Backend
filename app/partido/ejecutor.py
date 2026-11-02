import asyncio
from .motor import MotorPartido, T
from .convertidor import estado_a_dict, estados_jugadores_a_dict, eventos_a_dict
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones

DURACION_PAUSA = 30.0 # SEGUNDOS

class EjecutorPartido:

    def __init__(self, partido_id: int, motor: MotorPartido, duracion: float, duracion_pausa = DURACION_PAUSA, admin = admin_conexiones):
        self.partido_id = partido_id
        self.motor = motor
        self.duracion = duracion
        self.duracion_pausa = duracion_pausa
        self.pausado = False
        self.admin = admin

        self.tiempos_pausa = [ 
            self.duracion * 0.25, # pausa al primer cuarto del partido (cooling break)
            self.duracion * 0.5, # pausa de entretiempo
            self.duracion * 0.75 # pausa al tercer cuarto del partido (cooling break)
        ]
        self.pausas_realizadas = 0


    async def ejecutar(self):

        # avisamos que el partido comenzo
        await self.admin.emitir_partido(partido_id=self.partido_id, accion="partido_iniciado", payload={"tiempo": 0})

        # mandamos el estado inicial antes del primer tick
        await self.admin.emitir_partido(partido_id=self.partido_id, accion="estado_partido", payload={**estado_a_dict(self.motor.estado), "estados_jugadores": [], "acciones": []})

        while self.motor.estado.tiempo < self.duracion:

            estado, estados_jugadores, eventos = self.motor.tick()

            # envio el nuevo estado al front
            await self.admin.emitir_partido(
                partido_id=self.partido_id,
                accion="estado_partido",
                payload={** estado_a_dict(estado), "estados_jugadores": estados_jugadores_a_dict(estados_jugadores, estado), "acciones": eventos_a_dict(eventos)})

            if (self.pausas_realizadas < len(self.tiempos_pausa) and
                self.motor.estado.tiempo < self.duracion and 
                self.motor.estado.tiempo >= self.tiempos_pausa[self.pausas_realizadas] 
            ):
                self.pausas_realizadas += 1
                await self.pausar()
                await asyncio.sleep(self.duracion_pausa) 
                await self.reanudar()
            
            # esperamos hasta el proximo tick, esto es para que no se ejecuten instantaneamente varios ticks
            if self.motor.estado.tiempo < self.duracion: 
                await asyncio.sleep(T) 

        # avisamos que el partido termino
        await self.admin.emitir_partido(
            partido_id=self.partido_id,
            accion="partido_terminado",
            payload={
                "tiempo": self.motor.estado.tiempo,
                "goles": {"izquierdo": self.motor.estado.goles_izquierdo,
                          "derecho": self.motor.estado.goles_derecho}})
        
    async def pausar(self):
        if self.pausado:
            return  # ya esta en pausa, no hacemos nada
        
        self.pausado = True

        await self.admin.emitir_partido(
            partido_id=self.partido_id, 
            accion="partido_pausado", 
            payload={"tiempo": self.motor.estado.tiempo, "numero_pausa": self.pausas_realizadas, "duracion_pausa" : self.duracion_pausa}
        ) 

    async def reanudar(self): 
        if not self.pausado:
            return 
        
        self.pausado = False

        await self.admin.emitir_partido(
            partido_id=self.partido_id, 
            accion="partido_reanudado", 
            payload={"tiempo": self.motor.estado.tiempo}
        )