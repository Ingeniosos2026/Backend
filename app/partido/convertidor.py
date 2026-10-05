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

