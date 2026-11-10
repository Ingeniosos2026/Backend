from .estados import EstadoPartido, Cancha
from app.capa_0_definicion_bd.models.fixture_liga_modelos import FixtureLiga
from app.capa_0_definicion_bd.models.tabla_liga_modelos import TablaLiga

def estado_a_dict(estado: EstadoPartido) -> dict:
    jugadores = []
    suplentes = []

    for jugador in estado.jugadores.values():
        jugadores.append({
            "id_jugador": jugador.id_jugador,
            "id_usuario": jugador.id_usuario,
            "id_equipo": jugador.id_equipo,
            "nombre": jugador.nombre,
            "x": jugador.posicion.x,
            "y": jugador.posicion.y})
    
    for jugador in estado.suplentes.values():
        suplentes.append({
            "id_jugador": jugador.id_jugador,
            "id_usuario": jugador.id_usuario,
            "id_equipo": jugador.id_equipo,
            "nombre": jugador.nombre
        })

    return {
        "id_usuario_izquierdo":estado.id_usuario_izquierdo,
        "id_usuario_derecho":estado.id_usuario_derecho,
        "tiempo": estado.tiempo,
        "pelota": {
            "x": estado.pelota.posicion.x,
            "y": estado.pelota.posicion.y},
        "jugadores": jugadores,
        "suplentes": suplentes,
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

def fixture_a_dict(fixture: FixtureLiga) -> dict:
    return {
        "turno": fixture.turno,
        "id_partido": fixture.id_partido,
        "equipo_izq": {
            "id_equipo": fixture.equipo_izq.id_equipo,
            "nombre_club": fixture.equipo_izq.usuario.nombre_club,
            "id_usuario": fixture.equipo_izq.id_usuario},
        "equipo_der": {
            "id_equipo": fixture.equipo_der.id_equipo,
            "nombre_club": fixture.equipo_der.usuario.nombre_club,
            "id_usuario": fixture.equipo_der.id_usuario},
        "goles_izq": fixture.goles_equipo_izq,
        "goles_der": fixture.goles_equipo_der}

def tabla_a_dict(registro: TablaLiga) -> dict:
    return {
        "id_equipo": registro.id_equipo,
        "nombre_club": registro.usuario.nombre_club,
        "partidos_ganados": registro.partidos_ganados,
        "partidos_empatados": registro.partidos_empatados,
        "partidos_perdidos": registro.partidos_perdidos,
        "puntos": registro.puntos,
        "goles_a_favor": registro.goles_a_favor,
        "goles_en_contra": registro.goles_en_contra}

def cancha_a_dict(cancha: Cancha) -> dict:
    return {
        "ancho": cancha.ancho,
        "alto": cancha.alto,
        "arco_izquierdo": {
            "poste_superior": {"x": cancha.arco_izquierdo.poste_superior.x, "y": cancha.arco_izquierdo.poste_superior.y},
            "poste_inferior": {"x": cancha.arco_izquierdo.poste_inferior.x, "y": cancha.arco_izquierdo.poste_inferior.y}},
        "arco_derecho": {
            "poste_superior": {"x": cancha.arco_derecho.poste_superior.x, "y": cancha.arco_derecho.poste_superior.y},
            "poste_inferior": {"x": cancha.arco_derecho.poste_inferior.x, "y": cancha.arco_derecho.poste_inferior.y}}}