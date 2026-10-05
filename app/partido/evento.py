from dataclasses import dataclass


@dataclass
class EventoJugador:
    id_jugador: int
    id_usuario: int
    accion: str

# nos va a servir para representar las acciones de ese tick, queda medio feo un solo archivo para esto