import math
from .estados import Coordenada, JugadorEstado, Cancha


def calcular_distancia(a: Coordenada, b: Coordenada) -> float:
    # calcula la distancia entre dos coordenadas, se uso el famoso pitagoras para calcular la distancia entre 2 puntos
    return math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


def calcular_direccion(origen: Coordenada, destino: Coordenada) -> Coordenada:
    # se alcula la direccion normalizada desde origen hasta destino

    dx = destino.x - origen.x
    dy = destino.y - origen.y

    distancia = math.sqrt(dx ** 2 + dy ** 2)

    if distancia == 0:
        return Coordenada(0, 0)

    return Coordenada(x=dx / distancia, y=dy / distancia)


def calcular_alcance(control: int) -> float:
    # calcula la distancia maxima a la que un jugador
    # puede interactuar con la pelota segun su control (queda a definir, puse esto para probar)

    return 0.5 + control / 50


def calcular_tiempo_pateo(agilidad: int) -> float:
    # (queda a definir, puse esto para probar)
    # calcula el tiempo para patear
    #agilidad = 20 es equivalente 1.7 segundos
    #agilidad = 100 es equivalente 0.5 segundos

    return 2.0 - 0.015 * agilidad


def calcular_potencia(poder: int) -> float:
    # calcula la velocidad inicial de la pelota al patear
    # (queda a definir, puse esto para probar)   

    return 5.0 + poder * 0.05


def calcular_velocidad(velocidad: int) -> float:
    #(queda a definir, puse esto para probar)
    # calcula la velocidad de movimiento del jugador

    return 2.0 + velocidad / 25


def obtener_jugador(estado, id_usuario: int, id_jugador: int) -> JugadorEstado:
   
    #pbtiene un jugador del estado del partido
    clave = (id_usuario, id_jugador)

    if clave not in estado.jugadores:
        raise ValueError("El jugador no existe en el partido")

    return estado.jugadores[clave]


def posicion_valida(posicion: Coordenada, cancha: Cancha) -> bool:
    # la posicion tiene que estar dentro de la cancha
    return (0 <= posicion.x <= cancha.ancho and 0 <= posicion.y <= cancha.alto)


