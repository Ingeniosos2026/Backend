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

        # ejecutar el comportamiento de cada jugador 
        for clave, jugador in self.estado.jugadores.items(): 
            codigo = self.estado.comportamientos[clave] 
            ejecutar_comportamiento(estado=self.estado, jugador=jugador, codigo=codigo)
        
        # actualizar la fisica durante un periodo de tiempo T
        self.fisica.actualizar(T)

        # avanzar el tiempo del partido
        self.estado.tiempo += T

        # devolver el estado actualizado.
        return self.estado

