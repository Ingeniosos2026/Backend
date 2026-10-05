from .estados import EstadoPartido
from .fisicas import FisicaPartido
from .ejecutar_comportamiento import ejecutar_comportamiento

TICKS_POR_SEGUNDO = 30
T = 1 / TICKS_POR_SEGUNDO


class MotorPartido:
    def __init__(self, estado: EstadoPartido):
        self.estado = estado
        self.fisica = FisicaPartido(estado)

    def tick(self) -> EstadoPartido:
        eventos = []

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
    
