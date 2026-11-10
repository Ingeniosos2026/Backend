from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador
from app.capa_1_acceso_datos.repositorios.equipos import EquipoRepositorio
from app.capa_0_definicion_bd.models.equipos_jugadores_modelos import EstadoJugador, EquipoJugador



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
        nombre_jugador="Messi",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60
    )

    jugador2 = Jugador(
        id_usuario=usuario.id_usuario,
        nombre_jugador="Neymar",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60
    )

    db_test.add_all([jugador1, jugador2])
    db_test.commit()

    asociacion1 = EquipoJugador(
        equipo=equipo,
        jugador=jugador1,
        estado=EstadoJugador.TITULAR
    )

    asociacion2 = EquipoJugador(
        equipo=equipo,
        jugador=jugador2,
        estado=EstadoJugador.SUPLENTE
    )

    db_test.add_all([asociacion1, asociacion2])
    db_test.commit()

    db_test.refresh(equipo)

    assert len(equipo.jugadores) == 2
    assert equipo.jugadores[0].jugador == jugador1
    assert equipo.jugadores[1].jugador == jugador2
    assert equipo.jugadores[0].estado == EstadoJugador.TITULAR
    assert equipo.jugadores[1].estado == EstadoJugador.SUPLENTE

def test_agregar_jugador_a_equipo(db_test):
    usuario = Usuario(
        email="pepito@gmail.com",
        nombre="Pepito",
        id_avatar=2,
        contraseña="asd123",
        nombre_club="Boca"
    )
    db_test.add(usuario)
    db_test.commit()
    db_test.refresh(usuario)
    equipo = Equipo(id_usuario=usuario.id_usuario)
    db_test.add(equipo)
    db_test.commit()
    db_test.refresh(equipo)

    jugador = Jugador(
        id_usuario=usuario.id_usuario,
        nombre_jugador="Messi",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60,
    )
    db_test.add(jugador)
    db_test.commit()
    db_test.refresh(jugador)

    repositorio = EquipoRepositorio(db_test)
    repositorio.agregar_jugador(equipo, jugador, EstadoJugador.TITULAR)
    db_test.refresh(equipo)
    db_test.refresh(jugador)

    assert len(equipo.jugadores) == 1
    assert equipo.jugadores[0].jugador == jugador
    assert equipo.jugadores[0].estado == EstadoJugador.TITULAR

def test_jugador_en_dos_equipos(db_test):
    usuario = Usuario(
        email="pepito@gmail.com",
        nombre="Pepito",
        id_avatar=2,
        contraseña="asd123",
        nombre_club="Boca"
    )
    db_test.add(usuario)
    db_test.commit()
    db_test.refresh(usuario)

    equipo1 = Equipo(id_usuario=usuario.id_usuario)
    equipo2 = Equipo(id_usuario=usuario.id_usuario)

    db_test.add_all([equipo1, equipo2])
    db_test.commit()
    db_test.refresh(equipo1)
    db_test.refresh(equipo2)

    jugador = Jugador(
        id_usuario=usuario.id_usuario,
        nombre_jugador="Messi",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60
    )
    db_test.add(jugador)
    db_test.commit()
    db_test.refresh(jugador)

    repositorio = EquipoRepositorio(db_test)
    repositorio.agregar_jugador(equipo1, jugador,  EstadoJugador.TITULAR)
    db_test.refresh(equipo1)
    db_test.refresh(jugador)

    assert len(equipo1.jugadores) == 1
    assert equipo1.jugadores[0].jugador == jugador
    assert equipo1.jugadores[0].estado == EstadoJugador.TITULAR

    repositorio.agregar_jugador(equipo2, jugador,  EstadoJugador.TITULAR)
    db_test.refresh(equipo2)
    db_test.refresh(jugador)

    assert len(equipo2.jugadores) == 1
    assert equipo2.jugadores[0].jugador == jugador
    assert equipo2.jugadores[0].estado == EstadoJugador.TITULAR