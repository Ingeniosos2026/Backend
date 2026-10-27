import pytest

from app.capa_0_definicion_bd.models.liga_modelos import Liga, EstadoLiga
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador
from app.capa_1_acceso_datos.repositorios.ligas import LigaRepositorio
from app.capa_1_acceso_datos.repositorios.usuarios import UsuarioRepositorio
from app.capa_2_logica.errores import DatosLigaInvalidos
from app.capa_2_logica.servicios import Servicios

def create_usuario(session):
    usuario = Usuario(
        email="pepito@gmail.com",
        nombre="Pepito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="Boca",
    )

    session.add(usuario)
    session.commit()

    return usuario

def create_servicio(session):
    return Servicios(
        usuarios=UsuarioRepositorio(session),
        ligas=LigaRepositorio(session),
    )

def test_crear_liga(db_test):
    usuario = create_usuario(db_test)

    liga = Liga(
        id_usuario=usuario.id_usuario,
        nombre="Liga de prueba",
        contraseña="1234",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=3,
        max_jugadores=10,
        duracion_partido=10,
    )

    db_test.add(liga)
    db_test.commit()

    assert liga.id is not None
    assert liga.id_usuario == usuario.id_usuario
    assert liga.nombre == "Liga de prueba"
    assert liga.estado == EstadoLiga.DISPONIBLE
    assert liga.min_jugadores == 3
    assert liga.max_jugadores == 10
    assert liga.duracion_partido == 10

def test_min_jugadores_no_puede_ser_menor_a_3(db_test):
    usuario = create_usuario(db_test)
    servicio = create_servicio(db_test)

    with pytest.raises(DatosLigaInvalidos):
        servicio.crear_liga(
            usuario_id=usuario.id_usuario,
            nombre="Liga inválida",
            contraseña="1234",
            min_jugadores=2,
            max_jugadores=10,
            duracion_partido=10,
        )

def test_liga_sin_contraseña_es_valida(db_test):
    usuario = create_usuario(db_test)

    liga = Liga(
        id_usuario=usuario.id_usuario,
        nombre="Liga sin contraseña",
        contraseña=None,
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=3,
        max_jugadores=10,
        duracion_partido=10,
    )

    db_test.add(liga)
    db_test.commit()

    assert liga.id is not None
    assert liga.contraseña is None

def test_servicio_lista_solo_ligas_disponibles(db_test):
    usuario = create_usuario(db_test)
    liga_disponible = Liga(
        id_usuario=usuario.id_usuario,
        nombre="premier league",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=3,
        max_jugadores=10,
        duracion_partido=10,
    )
    liga_en_juego = Liga(
        id_usuario=usuario.id_usuario,
        nombre="superlgia",
        estado=EstadoLiga.EN_JUEGO,
        min_jugadores=3,
        max_jugadores=10,
        duracion_partido=10,
    )
    db_test.add_all([liga_disponible, liga_en_juego])
    db_test.commit()

    resultado = create_servicio(db_test).listar_ligas_disponibles()

    assert resultado.ligas == [liga_disponible]

def crear_jugadores_bd(db_test, usuario_id, cantidad=6):
    jugadores = [
        Jugador(id_usuario=usuario_id, nombre_jugador=f"Jug {i}", poder=60, agilidad=60, control=60, velocidad=60, fuerza=60)
        for i in range(cantidad)
    ]
    db_test.add_all(jugadores)
    db_test.commit()

def test_unirse_liga_publica(client, db_test):
    creador = create_usuario(db_test)
    usuario = client.post("/usuario", json={"email": "crack@gmail.com", "nombre": "tomas", "avatar": 1, "contraseña": "1", "club": "talleres"}).json()
    crear_jugadores_bd(db_test, usuario["id"], cantidad=6)

    liga = Liga(id_usuario=creador.id_usuario, nombre="ligapreba", estado=EstadoLiga.DISPONIBLE, min_jugadores=3, max_jugadores=5, duracion_partido=10)
    db_test.add(liga)
    db_test.commit()
    db_test.refresh(liga)

    response = client.put(f"/liga/{liga.id}/unirse/{usuario['id']}")
    assert response.status_code == 200
    
    db_test.refresh(liga)
    assert len(liga.participantes) == 1

def test_unirse_liga_con_contraseña(client, db_test):
    creador = create_usuario(db_test)
    usuario = client.post("/usuario", json={"email": "crack@gmail.com", "nombre": "tomas", "avatar": 1, "contraseña": "1", "club": "talleres"}).json()
    crear_jugadores_bd(db_test, usuario["id"], cantidad=6)

    liga = Liga(id_usuario=creador.id_usuario, nombre="ligapreba", contraseña="123", estado=EstadoLiga.DISPONIBLE, min_jugadores=3, max_jugadores=5, duracion_partido=10)
    db_test.add(liga)
    db_test.commit()

    responseFail = client.put(f"/liga/{liga.id}/unirse/{usuario['id']}", json={"contraseña": "000"})
    assert responseFail.status_code == 401

    responseOk = client.put(f"/liga/{liga.id}/unirse/{usuario['id']}", json={ "contraseña":"123"})
    assert responseOk.status_code == 200

def test_unirse_liga_jugadores_insuficientes(client, db_test):
    creador = create_usuario(db_test)
    usuario = client.post("/usuario", json={"email": "crack@gmail.com", "nombre": "tomas", "avatar": 1, "contraseña": "1", "club": "talleres"}).json()
    crear_jugadores_bd(db_test, usuario["id"], cantidad=5)

    liga = Liga(id_usuario=creador.id_usuario, nombre="Liga", estado=EstadoLiga.DISPONIBLE, min_jugadores=3, max_jugadores=5, duracion_partido=10)
    db_test.add(liga)
    db_test.commit()

    response = client.put(f"/liga/{liga.id}/unirse/{usuario['id']}")
    assert response.status_code == 400