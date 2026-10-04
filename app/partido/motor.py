from .estados import EstadoPartido
from .fisicas import FisicaPartido

TICKS_POR_SEGUNDO = 30
T = 1 / TICKS_POR_SEGUNDO


class MotorPartido:
    def __init__(self, estado: EstadoPartido):
        self.estado = estado
        self.fisica = FisicaPartido(estado)

    def tick(self) -> EstadoPartido:
        # actualizar la fisica durante un periodo de tiempo T
        self.fisica.actualizar(T)

        # avanzar el tiempo del partido
        self.estado.tiempo += T

        # devolver el estado actualizado.
        return self.estado

