from app.capa_0_definicion_bd.models.liga_modelos import Liga, EstadoLiga
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.tabla_liga_modelos import TablaLiga


def crear_usuario(session, email, nombre, club):
    usuario = Usuario(
        email=email,
        nombre=nombre,
        id_avatar=1,
        contraseña="aasdfg",
        nombre_club=club)

    session.add(usuario)
    session.commit()

    return usuario


def crear_equipo(session, usuario):
    equipo = Equipo(id_usuario=usuario.id_usuario)
    session.add(equipo)
    session.commit()

    return equipo


def crear_liga(session, usuario):
    liga = Liga(
        id_usuario=usuario.id_usuario,
        nombre="La mejor liga",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=3,
        max_jugadores=10,
        duracion_partido=10)

    session.add(liga)
    session.commit()

    return liga


def test_crear_tabla_liga(db_test):
    u1 = crear_usuario(db_test, "tomas@gmail.com", "Tomas", "Talleres")
    e1 = crear_equipo(db_test, u1)
    liga = crear_liga(db_test, u1)

    posicion = TablaLiga(
        id_liga=liga.id,
        id_equipo=e1.id_equipo,
        id_usuario=u1.id_usuario,
        partidos_ganados=2,
        partidos_empatados=1,
        partidos_perdidos=0,
        puntos=7,
        goles_a_favor=5,
        goles_en_contra=2)

    db_test.add(posicion)
    db_test.commit()

    assert posicion.id_liga == liga.id
    assert posicion.id_equipo == e1.id_equipo
    assert posicion.id_usuario == u1.id_usuario
    assert posicion.partidos_ganados == 2
    assert posicion.partidos_empatados == 1
    assert posicion.partidos_perdidos == 0
    assert posicion.puntos == 7
    assert posicion.goles_a_favor == 5
    assert posicion.goles_en_contra == 2
