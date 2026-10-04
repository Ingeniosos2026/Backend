from dataclasses import dataclass

@dataclass
class Coordenada:
    x: float
    y: float


@dataclass
class Arco:
    poste_superior: Coordenada
    poste_inferior: Coordenada

    @property
    def centro(self) -> Coordenada:
        return Coordenada(x=(self.poste_superior.x + self.poste_inferior.x)/2, y=(self.poste_superior.y + self.poste_inferior.y)/2)
    

@dataclass
class Cancha:
    ancho: float
    alto: float
    arco_izquierdo: Arco
    arco_derecho: Arco


@dataclass
class JugadorEstado:
    id_jugador: int
    id_equipo: int
    id_usuario: int

    posicion: Coordenada
    # atributos del jugador
    control: int
    agilidad: int
    fuerza: int
    poder: int
    velocidad: int

    destino: Coordenada | None = None
    ultimo_pateo: float = -10.0


@dataclass
class PelotaEstado:
    posicion: Coordenada   
    # la velocidad me indica la dirreccion de pateo y a que velocidad se patea, luego en el motor de fisicas 
    # se tendra que ver el tema de la friccion para que reduzca el la velocidad de pateo hasta que no avance mas
    velocidad: Coordenada

@dataclass
class EstadoPartido:
    id_usuario_izquierdo: int
    id_usuario_derecho: int
    id_equipo_izquierdo: int
    id_equipo_derecho: int
    cancha: Cancha
    jugadores: dict[tuple[int, int], JugadorEstado]
    pelota: PelotaEstado
    tiempo: float = 0.0
    goles_izquierdo: int = 0
    goles_derecho: int = 0






