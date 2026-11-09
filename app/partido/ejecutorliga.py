import asyncio 
import random
from .motor import MotorPartido, T 
from .convertidor import fixture_a_dict, tabla_a_dict, estado_a_dict, estados_jugadores_a_dict, eventos_a_dict
from app.capa_0_definicion_bd.base_datos_sqlalchemy import SessionLocal 
from app.capa_0_definicion_bd.models.partidos_modelos import EstadoPartido, Formacion 
from .motor import MotorPartido
from .ejecutor import EjecutorPartido 
from .estados import Coordenada, JugadorEstado  
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones 
from app.capa_3_api.dependencias import crear_servicio 
from .inicializacion import crear_estado_partido 
from app.partido.administrar_partidos import administrador_partidas 
from app.capa_2_logica.errores import NoSePuedeElegirComoArquero, SoloPuedenPatearLosTitulares

DURACION_PREPARACION_PENALES = 20.0  # SEGUNDOS
DURACION_PENAL = 20.0  # SEGUNDOS


class EjecutorLiga:

    def __init__(self, liga_id: int, partido_id: int, motor: MotorPartido, duracion: float,  ejecutor_partido: EjecutorPartido, penales: bool ,turno: int = 1):
        self.liga_id = liga_id
        self.partido_id = partido_id
        self.motor = motor
        self.duracion = duracion
        self.ejecutor_partido = ejecutor_partido
        self.turno = turno
        self.penales = not penales 
        self.config_penales: dict[int, dict] = {}
        self.esperando_config_penales: bool = False
        self.penales_izquierdo = 0
        self.penales_derecho = 0
        self.titulares_finales: dict[tuple[int, int], JugadorEstado] = {}

        #agregar un campo de BD para saber si es empate 
        
    async def ejecutar(self):
        # se crea una sesion propia para la ejecucion de la liga 
        db = SessionLocal()
        try:
            servicio = crear_servicio(db)
            while True:

                self.config_penales.clear()
                self.esperando_config_penales = False
                self.titulares_finales.clear()
                
                # ejecutamos el partido actual
                resultado_partido = await self.ejecutor_partido.ejecutar()
                goles_izq = resultado_partido["goles_izquierdo"]
                goles_der = resultado_partido["goles_derecho"]
                penales_izq = None
                penales_der = None
                id_ganador_penales = None

                # si termina en empate, definimos por penales
                if self.penales and goles_izq == goles_der:
                    administrador_partidas.agregar(partido_id=self.partido_id, ejecutor=self)
                    await self.ejecutar_tanda_penales()
                    penales_izq = self.penales_izquierdo
                    penales_der = self.penales_derecho

                    if penales_izq > penales_der:
                        id_ganador_penales = self.motor.estado.id_equipo_izquierdo
                        motivo_desempate = "penales"
                    elif penales_der > penales_izq:
                        id_ganador_penales = self.motor.estado.id_equipo_derecho
                        motivo_desempate = "penales"
                    else:
                        id_ganador_penales, motivo_desempate = self.desempatar_por_tabla_o_sorteo(servicio)

                    await admin_conexiones.emitir_partido(
                        partido_id=self.partido_id,
                        accion="partido_terminado_penales",
                        payload={
                            "tiempo": self.motor.estado.tiempo,
                            "goles": {"izquierdo": goles_izq, "derecho": goles_der},
                            "penales": {"izquierdo": penales_izq, "derecho": penales_der},
                            "ganador_id_equipo": id_ganador_penales,
                            "motivo_desempate": motivo_desempate
                        }
                    )
                    administrador_partidas.eliminar(self.partido_id)

                # registramos el resultado en la liga
                resultado_liga = servicio.registrar_resultado_partido_liga (id_liga=self.liga_id, turno=self.turno, goles_izq=resultado_partido["goles_izquierdo"], goles_der=resultado_partido["goles_derecho"], id_equipo_ganador_penales=id_ganador_penales)
                fixture = resultado_liga.fixture
                tabla_izq = resultado_liga.tabla_izq
                tabla_der = resultado_liga.tabla_der

                # notificamos el resultado y la tabla actualizada
                await admin_conexiones.emitir_lobby_liga(
                    liga_id=self.liga_id,
                    accion="resultado_partido",
                    payload={
                        "fixture": fixture_a_dict(fixture),
                        "tabla_actualizada": [tabla_a_dict(tabla_izq), tabla_a_dict(tabla_der)]})

                # buscamos y creamos el siguiente partido
                siguiente = servicio.crear_siguiente_partido_liga(id_liga=self.liga_id)

                # si no quedan partidos, finaliza la liga
                if siguiente.partido is None:
                    liga_fin = servicio.finalizar_liga(self.liga_id)

                    await admin_conexiones.emitir_lobby_liga(
                        liga_id=liga_fin.liga.id,
                        accion="liga_terminada",
                        payload={
                            "id_liga": liga_fin.liga.id,
                            "estado": "TERMINADA"})

                    break

                # se prepara el siguiente partido
                partido = siguiente.partido

                self.partido_id = partido.id_partido
                self.turno += 1

                estado = crear_estado_partido(partido)
                self.motor = MotorPartido(estado=estado)
                self.ejecutor_partido = EjecutorPartido(partido_id=partido.id_partido, motor=self.motor, duracion=self.duracion)
                administrador_partidas.agregar(partido_id=partido.id_partido, ejecutor=self.ejecutor_partido)

                await admin_conexiones.emitir_lobby_liga(
                        liga_id=self.liga_id,
                        accion="proximo_partido",
                        payload={"id_proximo_partido": self.partido_id, "turno":self.turno})

        finally:
            db.close()

    def obtener_ids_jugadores_en_cancha_usuario(self, estado: EstadoPartido, usuario_id: int) -> list[int]:
        enCancha = self.titulares_finales if self.titulares_finales else estado.jugadores
        return [j.id_jugador for (u_id, _), j in enCancha.items() if u_id == usuario_id]
    
    def configurar_penales_usuario(self,usuario_id: int,id_arquero: int,comportamiento_arquero: str,comportamiento_pateadores: list[tuple[int, str]],estado: EstadoPartido):

        ids_titulares = self.obtener_ids_jugadores_en_cancha_usuario(estado, usuario_id)
        if id_arquero not in ids_titulares:
            raise NoSePuedeElegirComoArquero()

        ids_pateadores = [id_j for id_j, _ in comportamiento_pateadores]
        if len(ids_pateadores) != 3 or set(ids_pateadores) != set(ids_titulares):
            raise SoloPuedenPatearLosTitulares()

        self.config_penales[usuario_id] = {
            "id_arquero": id_arquero,
            "comportamiento_arquero": comportamiento_arquero,
            "pateadores": comportamiento_pateadores
        }

    def obtener_config_usuario(self, estado: EstadoPartido, usuario_id: int, comportamientos_originales: dict) -> dict:
        if usuario_id in self.config_penales:
            return self.config_penales[usuario_id]
        
        # si el usuario no hace o se le acaba el tiempo, se elige esta configuracion por default
        ids_titulares = self.obtener_ids_jugadores_en_cancha_usuario(estado, usuario_id)
        primer_titular = ids_titulares[0]
        return {
            "id_arquero": primer_titular,
            "comportamiento_arquero": comportamientos_originales[(usuario_id, primer_titular)],
            "pateadores": [(id_j, comportamientos_originales[(usuario_id, id_j)]) for id_j in ids_titulares]
        }
    
    async def ejecutar_un_penal (self, lado_pateador: str, id_usuario_pateador: int, id_jugador_pateador: int,
                                comportamiento_pateador: str,id_usuario_arquero: int,id_jugador_arquero: int,
                                comportamiento_arquero: str) -> bool:

        estado = self.motor.estado
        cancha = estado.cancha
        centro_x = cancha.ancho / 2
        centro_y = cancha.alto / 2

        self.motor.fisica.en_penales = True
        self.motor.fisica.hubo_gol_penal = False
        self.motor.fisica.lado_pateador_penal = lado_pateador
        self.penales = True 

        estado.pelota.posicion = Coordenada(centro_x, centro_y)
        estado.pelota.velocidad = Coordenada(0, 0)

        if lado_pateador == "derecho":
            pos_pateador = Coordenada(centro_x + 3, centro_y)  # (53, 30)
            pos_arquero = Coordenada(cancha.arco_izquierdo.centro.x, cancha.arco_izquierdo.centro.y)  # (0, 30)
        else:
            pos_pateador = Coordenada(centro_x - 3, centro_y)  # (47, 30)
            pos_arquero = Coordenada(cancha.arco_derecho.centro.x, cancha.arco_derecho.centro.y)  # (100, 30)

        base_pateador = self.titulares_finales[(id_usuario_pateador, id_jugador_pateador)]
        base_arquero = self.titulares_finales[(id_usuario_arquero, id_jugador_arquero)]

        jugador_pateador = JugadorEstado(
          id_jugador=base_pateador.id_jugador, id_equipo=base_pateador.id_equipo,
          id_usuario=base_pateador.id_usuario, nombre=base_pateador.nombre, posicion=pos_pateador,
          control=base_pateador.control, agilidad=base_pateador.agilidad,
          fuerza=base_pateador.fuerza, poder=base_pateador.poder, velocidad=base_pateador.velocidad
        )
        jugador_arquero = JugadorEstado(
          id_jugador=base_arquero.id_jugador, id_equipo=base_arquero.id_equipo,
          id_usuario=base_arquero.id_usuario, nombre=base_arquero.nombre, posicion=pos_arquero,
          control=base_arquero.control, agilidad=base_arquero.agilidad,
          fuerza=base_arquero.fuerza, poder=base_arquero.poder, velocidad=base_arquero.velocidad
      )

        clave_pateador = (id_usuario_pateador, id_jugador_pateador) 
        clave_arquero = (id_usuario_arquero, id_jugador_arquero)

        # se actualizan los jugadores y comportamientos en el estado del partido
        estado.jugadores = {clave_pateador: jugador_pateador, clave_arquero: jugador_arquero} 
        estado.comportamientos = {clave_pateador: comportamiento_pateador, clave_arquero: comportamiento_arquero}

        tiempo_inicio_penal = estado.tiempo
  
        while (estado.tiempo - tiempo_inicio_penal) < DURACION_PENAL:

            estado, estados_jugadores, eventos = self.motor.tick()

            await admin_conexiones.emitir_partido(
                partido_id=self.partido_id,
                accion="estado_partido",
                payload={
                    **estado_a_dict(estado),
                    "estados_jugadores": estados_jugadores_a_dict(estados_jugadores, estado),
                    "acciones": eventos_a_dict(eventos),
                    "penales": {
                        "izquierdo": self.penales_izquierdo,
                        "derecho": self.penales_derecho,
                        "pateador_actual": id_jugador_pateador,
                        "arquero_actual": id_jugador_arquero,
                    },
                },
            )

            if self.motor.fisica.hubo_gol_penal:
                if lado_pateador == "derecho":
                    self.penales_derecho += 1
                else:
                    self.penales_izquierdo += 1
                    
                self.motor.fisica.en_penales = False
                return True

            # si no hubo gol, se espera hasta que termine el tiepmo del penal
            if (estado.tiempo - tiempo_inicio_penal) < DURACION_PENAL:
                await asyncio.sleep(T)

        self.motor.fisica.en_penales = False
        return False
    
    # devuelve la tupla donde especifica el motivo del desempate
    def desempatar_por_tabla_o_sorteo(self, servicio) -> tuple[int, str]:
        estado = self.motor.estado
        id_eq_izq = estado.id_equipo_izquierdo
        id_eq_der = estado.id_equipo_derecho

        tabla_izq = servicio.ligas.obtener_registro_tabla(self.liga_id, id_eq_izq)
        tabla_der = servicio.ligas.obtener_registro_tabla(self.liga_id, id_eq_der)

        # desempate por puntos en tabla 
        if tabla_izq is not None and tabla_der is not None: 
            if tabla_izq.puntos > tabla_der.puntos:
                return id_eq_izq, "ventaja_deportiva"
            if tabla_der.puntos > tabla_izq.puntos:
                return id_eq_der, "ventaja_deportiva"

            dif_izq = tabla_izq.goles_a_favor - tabla_izq.goles_en_contra
            dif_der = tabla_der.goles_a_favor - tabla_der.goles_en_contra

            # desempate por diferencia de goles
            if dif_izq > dif_der: 
                return id_eq_izq, "ventaja_deportiva"
            if dif_der > dif_izq:
                return id_eq_der, "ventaja_deportiva"
            
            # desempate por goles a favor
            if tabla_izq.goles_a_favor > tabla_der.goles_a_favor: 
                return id_eq_izq, "ventaja_deportiva"
            if tabla_der.goles_a_favor > tabla_izq.goles_a_favor:
                return id_eq_der, "ventaja_deportiva"

        # si hay un empate en la tabla o riecien en la fecha 1 se define de manera random
        ganador_azar = random.choice([id_eq_izq, id_eq_der])
        return ganador_azar, "sorteo del chiqui"
    
    async def ejecutar_tanda_penales(self):
        estado = self.motor.estado
        self.titulares_finales = dict(estado.jugadores)
        comportamientos_finales = dict(estado.comportamientos)
        self.esperando_config_penales = True

        self.penales_izquierdo = 0
        self.penales_derecho = 0

        await admin_conexiones.emitir_partido(
            partido_id= self.partido_id,
            accion= "inicio_definicion_penales",
            payload={
                "tiempo_espera": DURACION_PREPARACION_PENALES,
                "goles": {"izquierdo": estado.goles_izquierdo, "derecho": estado.goles_derecho}
            }
        )

        await asyncio.sleep(DURACION_PREPARACION_PENALES)
        self.esperando_config_penales = False

        # se obtiene la config de penales de cada usuario
        id_izq = estado.id_usuario_izquierdo
        id_der = estado.id_usuario_derecho
        
        config_izq = self.obtener_config_usuario(estado, id_izq, comportamientos_finales)
        config_der = self.obtener_config_usuario(estado, id_der, comportamientos_finales)

        for id_pateador, comportamiento_pateador in config_der["pateadores"]:
            await self.ejecutar_un_penal(
                lado_pateador="derecho", 
                id_usuario_pateador=id_der, 
                id_jugador_pateador=id_pateador,
                comportamiento_pateador=comportamiento_pateador, 
                id_usuario_arquero=id_izq,
                id_jugador_arquero=config_izq["id_arquero"], 
                comportamiento_arquero=config_izq["comportamiento_arquero"]
            )

        for id_pateador, comportamiento_pateador in config_izq["pateadores"]:
            await self.ejecutar_un_penal(
                lado_pateador="izquierdo", 
                id_usuario_pateador=id_izq, 
                id_jugador_pateador=id_pateador,
                comportamiento_pateador=comportamiento_pateador, 
                id_usuario_arquero=id_der,
                id_jugador_arquero=config_der["id_arquero"], 
                comportamiento_arquero=config_der["comportamiento_arquero"]
            )