import asyncio
from .motor import MotorPartido, T
from .convertidor import estado_a_dict, estados_jugadores_a_dict, eventos_a_dict, cancha_a_dict
from app.capa_0_definicion_bd.base_datos_sqlalchemy import SessionLocal
from app.capa_0_definicion_bd.models.partidos_modelos import EstadoPartido, TipoPartido
from app.capa_2_logica.resultados import CambioJugadorResultado
from app.capa_2_logica.errores import NoSePuedeCambiarJugador
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones
from app.capa_3_api.dependencias import crear_servicio
from .administrar_partidos import administrador_partidas
from .estados import Coordenada, JugadorEstado


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
        self.equipos_que_cambiaron = set()
        self.cambios_pendientes = {}
        self.comportamientos_pendientes = {}


    async def ejecutar(self):

        # avisamos que el partido comenzo
        await self.admin.emitir_partido(partido_id=self.partido_id, accion="partido_iniciado", payload={"tiempo": 0})

        # mandamos el estado inicial antes del primer tick
        await self.admin.emitir_partido(partido_id=self.partido_id, accion="estado_partido", payload={**estado_a_dict(self.motor.estado), "estados_jugadores": [], "acciones": [], "cancha": cancha_a_dict(self.motor.estado.cancha)})

        while self.motor.estado.tiempo < self.duracion:
            self.cambio_comportamientos_pendientes()

            estado, estados_jugadores, eventos = self.motor.tick()

            # envio el nuevo estado al front
            await self.admin.emitir_partido(
                partido_id=self.partido_id,
                accion="estado_partido",
                payload={** estado_a_dict(estado), "estados_jugadores": estados_jugadores_a_dict(estados_jugadores, estado), "acciones": eventos_a_dict(eventos)})
    

            if (self.pausas_realizadas < len(self.tiempos_pausa) and self.motor.estado.tiempo < self.duracion and self.motor.estado.tiempo >= self.tiempos_pausa[self.pausas_realizadas]):
                await self.pausar()
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
                raise ValueError("No se encontro el partido")

            if partido.tipo_partido == TipoPartido.AMISTOSO:
                servicio.registrar_resultado_amistoso(
                    partido_id=self.partido_id,
                    goles_izq=goles_izquierdo,
                    goles_der=goles_derecho)
            else:
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
        
        administrador_partidas.eliminar(self.partido_id)
        
        return {"goles_izquierdo": goles_izquierdo, "goles_derecho": goles_derecho}
        
    async def pausar(self):
        if self.pausado:
            return  # ya esta en pausa, no hacemos nada
        
        self.pausado = True
        self.pausas_realizadas += 1

        if (self.pausas_realizadas == 2):
            tiempo_espera = self.duracion_pausa_entretiempo
            self.motor.fisica.reiniciar_posiciones()
        else:
            tiempo_espera = self.duracion_pausa_cooling_break
        
        await self.procesar_cambios_pendientes()
        
        await self.admin.emitir_partido(
        partido_id=self.partido_id, 
        accion="partido_pausado", 
        payload={"tiempo": self.motor.estado.tiempo, "numero_pausa": self.pausas_realizadas, "duracion_pausa" : tiempo_espera}
        ) 

            
        
        await asyncio.sleep(tiempo_espera)

    async def reanudar(self): 
        if not self.pausado:
            return 
        
        self.pausado = False

        await self.admin.emitir_partido(
            partido_id=self.partido_id, 
            accion="partido_reanudado", 
            payload={"tiempo": self.motor.estado.tiempo}
        )

    # esto comproueba si puedo cambiar o no en una pasa
    def puede_realizar_cambio(self, id_equipo: int) -> bool:

        if not self.pausado:
            return False

        if not 1 <= self.pausas_realizadas <= 3:
            return False

        if (self.pausas_realizadas, id_equipo) in self.equipos_que_cambiaron:
            return False

        return True
    
    async def solicitar_cambio(self, usuario_id: int, jugador_sale_id: int, resultado: CambioJugadorResultado):
        estado = self.motor.estado

        # busco al equipo
        if usuario_id == estado.id_usuario_izquierdo:
            id_equipo = estado.id_equipo_izquierdo

        elif usuario_id == estado.id_usuario_derecho:
            id_equipo = estado.id_equipo_derecho

        else:
            raise NoSePuedeCambiarJugador()
    
        # se verifica que tenga cambios
        total_cambios = 0
        for _, equipo in self.equipos_que_cambiaron:
            if equipo == id_equipo:
                total_cambios += 1

        if total_cambios >= 3:
            raise NoSePuedeCambiarJugador()

        # si esta en una pausa, realizp el cambio
        if self.pausado:
            await self.realizar_cambio(usuario_id=usuario_id, id_equipo=id_equipo, jugador_sale_id=jugador_sale_id, resultado=resultado)
            return

        # si el partido esta en juego, guardo el cambio. si ya habia uno de antes lo piso (queda el ultimo cambio solicitado)
        self.cambios_pendientes[id_equipo] = (usuario_id, jugador_sale_id, resultado)
    
    async def realizar_cambio(self, usuario_id: int, id_equipo:int, jugador_sale_id: int, resultado: CambioJugadorResultado):
        # compruebo que el equipo pueda realizar un cambio
        if not self.puede_realizar_cambio(id_equipo):
            raise NoSePuedeCambiarJugador()

        estado = self.motor.estado
        # busco al jugador
        clave_sale = (usuario_id, jugador_sale_id)
        jugador_sale = estado.jugadores.get(clave_sale)

        # veo que el jugador que sale si esta en cancha, so no esta en la cancha no puedo hacer el cambio
        if jugador_sale is None:
            raise NoSePuedeCambiarJugador()


        clave_entra = (usuario_id, resultado.id_jugador)

        # compruebo que el jugador que entra no esta jugando
        if clave_entra in estado.jugadores:
            raise NoSePuedeCambiarJugador()

        # copio la posicion del jugador que sale
        posicion = jugador_sale.posicion
        nueva_posicion = Coordenada(x=posicion.x, y=posicion.y)

        # creo el estado del jugador que entra
        nuevo_jugador = JugadorEstado(
            id_jugador=resultado.id_jugador,
            id_equipo=id_equipo,
            id_usuario=usuario_id,
            nombre=resultado.nombre,
            posicion=nueva_posicion,
            control=resultado.control,
            agilidad=resultado.agilidad,
            fuerza=resultado.fuerza,
            poder=resultado.poder,
            velocidad=resultado.velocidad)

        # realizo el remplazo en memoria
        # elimino al jugador del partido
        del estado.jugadores[clave_sale]
        del estado.comportamientos[clave_sale]
        
        #ingreso al nuevo
        estado.jugadores[clave_entra] = nuevo_jugador
        estado.comportamientos[clave_entra] = resultado.codigo_comportamiento

        # registro que el equipo realizo  un cambio en esta pausa 
        self.equipos_que_cambiaron.add((self.pausas_realizadas, id_equipo))

        await self.admin.emitir_partido(
            partido_id=self.partido_id,
            accion="cambio_jugador_realizado",
            payload={
                "id_equipo": id_equipo,
                "id_usuario": usuario_id,
                "jugador_sale_id": jugador_sale_id,
                "jugador_entra_id":resultado.id_jugador})

    async def procesar_cambios_pendientes(self):
        for id_equipo, cambio in list(self.cambios_pendientes.items()):

            usuario_id, jugador_sale_id, resultado = cambio

            # elimino de cambios pendientes
            del self.cambios_pendientes[id_equipo]
            
            try:
                # realizo el cambio pendiente
                await self.realizar_cambio(usuario_id=usuario_id, id_equipo=id_equipo, jugador_sale_id=jugador_sale_id, resultado=resultado)

            except NoSePuedeCambiarJugador:
                continue

    
    def solicitar_cambio_comportamiento(self, usuario_id: int, jugador_id: int, comportamiento: str):
        clave = (usuario_id, jugador_id)
        self.comportamientos_pendientes[clave] = comportamiento

    def cambio_comportamientos_pendientes(self):
        for clave, comportamiento in self.comportamientos_pendientes.items():
            self.motor.estado.comportamientos[clave] = comportamiento

        self.comportamientos_pendientes.clear()