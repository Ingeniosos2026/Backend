from .estados import EstadoPartido
from .fisicas import FisicaPartido
from .ejecutar_comportamiento import ejecutar_comportamiento
from .ejecutar_comportamiento_dt import ejecutar_comportamiento_dt

TICKS_POR_SEGUNDO = 30
T = 1 / TICKS_POR_SEGUNDO


class MotorPartido:
    def __init__(self, estado: EstadoPartido):
        self.estado = estado
        self.fisica = FisicaPartido(estado)

    def tick(self) -> EstadoPartido:
        eventos = []

        self.ejecutar_dt()
        # ejecutar el comportamiento de cada jugador 
        for clave, jugador in self.estado.jugadores.items(): 
            codigo = self.estado.comportamientos[clave] 
            ejecutar_comportamiento(estado=self.estado, jugador=jugador, codigo=codigo, eventos=eventos)
        
        # actualizar la fisica durante un periodo de tiempo T
        self.fisica.actualizar(T)

        # avanzar el tiempo del partido
        self.estado.tiempo += T

        estados_jugadores = {}

        for clave, jugador in self.estado.jugadores.items(): 
            if jugador.destino is not None: 
                estado_jugador = "corriendo" 
            else: 
                estado_jugador = "quieto"   
            
            estados_jugadores[clave] = estado_jugador

        # devolver el estado actualizado.
        return self.estado, estados_jugadores, eventos
    
    def ejecutar_dt(self) -> None:
        for id_usuario, activo in self.estado.dt_activo.items():
            if activo:
                codigo = self.estado.codigo_dt[id_usuario]
                ejecutar_comportamiento_dt(estado=self.estado, id_usuario=id_usuario, codigo=codigo, posiciones_iniciales=self.fisica.posiciones_iniciales)