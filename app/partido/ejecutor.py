import asyncio
from .motor import MotorPartido, T
from .convertidor import estado_a_dict, estados_jugadores_a_dict, eventos_a_dict, cancha_a_dict
from app.capa_0_definicion_bd.base_datos_sqlalchemy import SessionLocal
from app.capa_0_definicion_bd.models.partidos_modelos import EstadoPartido
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones
from app.capa_3_api.dependencias import crear_servicio
from .administrar_partidos import administrador_partidas


DURACION_PAUSA_ENTRETIEMPO = 20.0 # SEGUNDOS
DURACION_PAUSA_COOLING_BREAK = 10.0 # SEGUNDOS

class EjecutorPartido:

    def __init__(self, partido_id: int, motor: MotorPartido, duracion: float, duracion_pausa_entretiempo = DURACION_PAUSA_ENTRETIEMPO,duracion_pausa_cooling_break = DURACION_PAUSA_COOLING_BREAK, admin = admin_conexiones):
        self.partido_id = partido_id
        self.motor = motor
        self.duracion = duracion
        self.duracion_pausa_entretiempo = duracion_pausa_entretiempo
        self.duracion_pausa_cooling_break = duracion_pausa_cooling_break
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
        await admin_conexiones.emitir_partido(partido_id=self.partido_id, accion="estado_partido", payload={**estado_a_dict(self.motor.estado), "estados_jugadores": [], "acciones": [], "cancha": cancha_a_dict(self.motor.estado.cancha)})

        while self.motor.estado.tiempo < self.duracion:

            estado, estados_jugadores, eventos = self.motor.tick()

            # envio el nuevo estado al front
            await self.admin.emitir_partido(
                partido_id=self.partido_id,
                accion="estado_partido",
                payload={** estado_a_dict(estado), "estados_jugadores": estados_jugadores_a_dict(estados_jugadores, estado), "acciones": eventos_a_dict(eventos)})
    

            if (self.pausas_realizadas < len(self.tiempos_pausa) and self.motor.estado.tiempo < self.duracion and self.motor.estado.tiempo >= self.tiempos_pausa[self.pausas_realizadas]):

                if (self.pausas_realizadas == 1):
                    tiempo_pausa = self.duracion_pausa_entretiempo
                else:
                    tiempo_pausa = self.duracion_pausa_cooling_break
                
                await self.pausar()
                self.pausas_realizadas += 1
                await asyncio.sleep(tiempo_pausa)
                await self.reanudar()

            # esperamos hasta el proximo tick, esto es para que no se ejecuten instantaneamente varios ticks
            if self.motor.estado.tiempo < self.duracion: 
                await asyncio.sleep(T) 
        
        # obtenemos el resultado final del partido
        goles_izquierdo = self.motor.estado.goles_izquierdo
        goles_derecho = self.motor.estado.goles_derecho

        # se actualiza el estado del partido en la base de datos
        db = SessionLocal()
        try:
            servicio = crear_servicio(db)
            partido = servicio.partidos.obtener_por_id(self.partido_id)

            if partido is None:
                raise ValueError("No se encontró el partido")

            partido.estado_partido = EstadoPartido.TERMINADO
            servicio.partidos.actualizar(partido)

        finally:
                db.close()

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
        
        if (self.pausas_realizadas == 1):
            tiempo_espera = self.duracion_pausa_entretiempo
        else:
            tiempo_espera = self.duracion_pausa_cooling_break

        await self.admin.emitir_partido(
        partido_id=self.partido_id, 
        accion="partido_pausado", 
        payload={"tiempo": self.motor.estado.tiempo, "numero_pausa": self.pausas_realizadas, "duracion_pausa" : tiempo_espera}
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
        administrador_partidas.eliminar(self.partido_id)
        
        return {"goles_izquierdo": goles_izquierdo, "goles_derecho": goles_derecho}
