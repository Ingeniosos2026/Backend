from app.capa_0_definicion_bd.base_datos_sqlalchemy import SessionLocal
from app.partido.administrar_partidos import administrador_partidas
from app.capa_3_api.dependencias import crear_servicio

from .motor import MotorPartido
from .ejecutor import EjecutorPartido
from .inicializacion import crear_estado_partido
from .convertidor import fixture_a_dict, tabla_a_dict

from app.capa_3_api.websockets.admin_conexiones import admin_conexiones


class EjecutorLiga:

    def __init__(self, liga_id: int, partido_id: int, motor: MotorPartido, duracion: float, turno: int = 1):
        self.liga_id = liga_id
        self.partido_id = partido_id
        self.motor = motor
        self.duracion = duracion
        self.turno = turno

    async def ejecutar(self):
        # se crea una sesion propia para la ejecucion de la liga 
        db = SessionLocal()
        try:
            servicio = crear_servicio(db)
            while True:

                # ejecutamos el partido actual
                ejecutor_partido = EjecutorPartido(partido_id=self.partido_id, motor=self.motor, duracion=self.duracion)

                resultado_partido = await ejecutor_partido.ejecutar()

                # registramos el resultado en la liga
                resultado_liga = servicio.registrar_resultado_partido_liga(id_liga=self.liga_id, turno=self.turno, goles_izq=resultado_partido["goles_izquierdo"], goles_der=resultado_partido["goles_derecho"])
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

                # buscamos y reamos el siguiente partido
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
                administrador_partidas.agregar(partido_id=partido.id_partido, motor=self.motor)

        finally:
            db.close()
