from app.capa_0_definicion_bd.models.liga_modelos import Liga, EstadoLiga
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.fixture_liga_modelos import FixtureLiga


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


def crear_fixture(session):
    usuario_1 = crear_usuario(session, "tomas@gmail.com", "Tomas", "Talleres")
    usuario_2 = crear_usuario(session, "jere@gmail.com", "Jere", "Belgrano")

    equipo_1 = crear_equipo(session, usuario_1)
    equipo_2 = crear_equipo(session, usuario_2)

    liga = crear_liga(session, usuario_1)

    return usuario_1, usuario_2, equipo_1, equipo_2, liga


def test_crear_fixture_liga(db_test):
    _, _, e1, e2, liga = crear_fixture(db_test)

    fixture = FixtureLiga(
        id_liga=liga.id,
        id_equipo_izq=e1.id_equipo,
        id_equipo_der=e2.id_equipo,
        turno=1,
    )

    db_test.add(fixture)
    db_test.commit()

    assert fixture.id_fixture is not None
    assert fixture.id_liga == liga.id
    assert fixture.id_equipo_izq == e1.id_equipo
    assert fixture.id_equipo_der == e2.id_equipo
    assert fixture.turno == 1
    assert fixture.id_partido is None