from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador, EstadoJugador


def test_crear_equipo_bd(db_test):
    usuario = Usuario(
        email="famaf.ingeniosos@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="Ingenieria-la-mejor-materia",
        nombre_club="Talleres"
    )

    db_test.add(usuario)
    db_test.commit()

    equipo = Equipo(id_usuario=usuario.id_usuario)

    db_test.add(equipo)
    db_test.commit()
    db_test.refresh(equipo)

    assert equipo.id_equipo is not None
    assert equipo.id_usuario == usuario.id_usuario


def test_equipo_puede_tener_jugadores_bd(db_test):
    usuario = Usuario(
        email="famaf.ingeniosos@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="Ingenieria-la-mejor-materia",
        nombre_club="Talleres"
    )

    db_test.add(usuario)
    db_test.commit()
  
    equipo = Equipo(id_usuario=usuario.id_usuario)

    db_test.add(equipo)
    db_test.commit()

    jugador1 = Jugador(
        id_usuario=usuario.id_usuario,
        id_equipo=equipo.id_equipo,
        nombre_jugador="Messi",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60,
        estado=EstadoJugador.TITULAR
    )

    jugador2 = Jugador(
        id_usuario=usuario.id_usuario,
        id_equipo=equipo.id_equipo,
        nombre_jugador="Neymar",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60,
        estado=EstadoJugador.SUPLENTE
    )

    db_test.add_all([jugador1, jugador2])
    db_test.commit()

    db_test.refresh(equipo)

    assert len(equipo.jugadores) == 2
    assert jugador1 in equipo.jugadores
    assert jugador2 in equipo.jugadores
    assert jugador1.estado == EstadoJugador.TITULAR
    assert jugador2.estado == EstadoJugador.SUPLENTE