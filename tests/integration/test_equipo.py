from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador, EstadoJugador
from app.capa_1_acceso_datos.repositorios.equipos import EquipoRepositorio


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
        estado=EstadoJugador.NINGUNO
    )
    db_test.add(jugador)
    db_test.commit()
    db_test.refresh(jugador)

    repositorio = EquipoRepositorio(db_test)
    repositorio.agregar_jugador(equipo, jugador)
    db_test.refresh(equipo)
    db_test.refresh(jugador)

    assert jugador.id_equipo == equipo.id_equipo
    assert jugador in equipo.jugadores_amistosos

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
        velocidad=60,
        estado=EstadoJugador.NINGUNO
    )
    db_test.add(jugador)
    db_test.commit()
    db_test.refresh(jugador)

    repositorio = EquipoRepositorio(db_test)
    repositorio.agregar_jugador(equipo1, jugador)
    db_test.refresh(equipo1)
    db_test.refresh(jugador)

    assert jugador.id_equipo == equipo1.id_equipo
    assert jugador in equipo1.jugadores_amistosos

    repositorio.agregar_jugador(equipo2, jugador)
    db_test.refresh(equipo2)
    db_test.refresh(jugador)

    assert jugador.id_equipo == equipo2.id_equipo
    assert jugador in equipo2.jugadores_amistosos