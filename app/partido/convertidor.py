from .estados import EstadoPartido


def estado_a_dict(estado: EstadoPartido) -> dict:
    jugadores = []

    for jugador in estado.jugadores.values():
        jugadores.append({
            "id_jugador": jugador.id_jugador,
            "id_usuario": jugador.id_usuario,
            "id_equipo": jugador.id_equipo,
            "x": jugador.posicion.x,
            "y": jugador.posicion.y})

    return {
        "tiempo": estado.tiempo,
        "pelota": {
            "x": estado.pelota.posicion.x,
            "y": estado.pelota.posicion.y},
        "jugadores": jugadores,
        "goles": {
            "izquierdo": estado.goles_izquierdo,
            "derecho": estado.goles_derecho}}

def estados_jugadores_a_dict(estados_jugadores, estado):
    resultado = []

    for clave, estado_jugador in estados_jugadores.items():

        jugador = estado.jugadores[clave]

        resultado.append({
            "id_jugador": jugador.id_jugador,
            "id_usuario": jugador.id_usuario,
            "estado": estado_jugador
        })

    return resultado


def eventos_a_dict(eventos):
    return [
        {
            "id_jugador": evento.id_jugador,
            "id_usuario": evento.id_usuario,
            "accion": evento.accion
        }
        for evento in eventos
    ]