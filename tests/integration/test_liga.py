import pytest

from app.capa_0_definicion_bd.models.liga_modelos import Liga, EstadoLiga
from app.capa_0_definicion_bd.models.liga_participantes_modelos import LigaParticipante
from app.capa_0_definicion_bd.models.tabla_liga_modelos import TablaLiga
from app.capa_0_definicion_bd.models.fixture_liga_modelos import FixtureLiga
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion
from app.capa_1_acceso_datos.repositorios.ligas import LigaRepositorio
from app.capa_1_acceso_datos.repositorios.usuarios import UsuarioRepositorio
from app.capa_2_logica.errores import DatosLigaInvalidos
from app.capa_2_logica.servicios import Servicios

def create_usuario(session, email = "pepito@gmail.com"):
    usuario = Usuario(
        email=email,
        nombre="Pepito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="Boca",
    )

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
        nombre="Liga de prueba",
        contraseña="1234",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=2,
        max_jugadores=4,
        duracion_partido=10)

    session.add(liga)
    session.commit()

    return liga

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

def test_abandonar_liga(client, db_test):
    creador = create_usuario(db_test)
    usuario = client.post("/usuario", json={
        "email": "crack@gmail.com", "nombre": "tomas", "avatar": 1, "contraseña": "1", "club": "talleres"
    }).json()
    crear_jugadores_bd(db_test, usuario["id"], cantidad = 6)

    liga = Liga(
        id_usuario = creador.id_usuario,
        nombre = "chiqui league",
        estado = EstadoLiga.DISPONIBLE,
        min_jugadores = 3,
        max_jugadores = 5,
        duracion_partido = 10,
    )
    db_test.add(liga)
    db_test.commit()
    db_test.refresh(liga)

    res_unirse = client.put(f"/liga/{liga.id}/unirse/{usuario['id']}")
    assert res_unirse.status_code == 200
    db_test.refresh(liga)
    assert len(liga.participantes) == 1

    res_abandonar = client.put(f"/liga/{liga.id}/abandonar/{usuario['id']}")
    assert res_abandonar.status_code == 200
    assert res_abandonar.json()["id_liga"] == liga.id
    assert res_abandonar.json()["id_usuario"] == usuario["id"]

    db_test.refresh(liga)
    assert len(liga.participantes) == 0


def test_abandonar_liga_rechaza_si_liga_ya_iniciada(client, db_test):
    creador = create_usuario(db_test)
    usuario_bd = Usuario(
        email = "crack@gmail.com", nombre = "Tomas", id_avatar = 1, contraseña = "1", nombre_club = "Talleres"
    )
    db_test.add(usuario_bd)
    db_test.commit()

    liga = Liga(
        id_usuario = creador.id_usuario,
        nombre = "chiqui league",
        estado = EstadoLiga.EN_JUEGO,
        min_jugadores = 3,
        max_jugadores = 5,
        duracion_partido = 10,
    )
    liga.participantes.append(usuario_bd)
    db_test.add(liga)
    db_test.commit()
    db_test.refresh(liga)

    response = client.put(f"/liga/{liga.id}/abandonar/{usuario_bd.id_usuario}")
    assert response.status_code == 409
    assert response.json()["error"] == "LIGA_INICIADA"

    db_test.refresh(liga)
    assert len(liga.participantes) == 1


def test_obtener_participantes_liga(db_test):
    usuario = create_usuario(db_test)
    usuario2 = create_usuario(db_test, email="pepito2@gmail.com")
    liga = crear_liga(db_test, usuario)

    equipo_1 = crear_equipo(db_test, usuario)
    equipo_2 = crear_equipo(db_test, usuario2)

    participante_1 = LigaParticipante(
        id_liga=liga.id,
        id_usuario=usuario.id_usuario,
        id_equipo=equipo_1.id_equipo,
        formacion=Formacion.DEFENSIVA)

    participante_2 = LigaParticipante(
        id_liga=liga.id,
        id_usuario=usuario2.id_usuario,
        id_equipo=equipo_2.id_equipo,
        formacion=Formacion.DEFENSIVA)

    db_test.add_all([participante_1, participante_2])
    db_test.commit()

    repositorio = LigaRepositorio(db_test)

    resultado = repositorio.obtener_participantes_liga(liga.id)

    assert len(resultado) == 2
    assert participante_1 in resultado
    assert participante_2 in resultado

def test_guardar_inicio_liga(db_test):
    usuario = create_usuario(db_test)
    usuario2 = create_usuario(db_test, email="pepito2@gmail.com")

    liga = crear_liga(db_test, usuario)

    equipo_1 = crear_equipo(db_test, usuario)
    equipo_2 = crear_equipo(db_test, usuario2)

    tabla_1 = TablaLiga(
        id_liga=liga.id,
        id_equipo=equipo_1.id_equipo,
        id_usuario=usuario.id_usuario,
        partidos_ganados=0,
        partidos_empatados=0,
        partidos_perdidos=0,
        puntos=0,
        goles_a_favor=0,
        goles_en_contra=0)

    tabla_2 = TablaLiga(
        id_liga=liga.id,
        id_equipo=equipo_2.id_equipo,
        id_usuario=usuario2.id_usuario,
        partidos_ganados=0,
        partidos_empatados=0,
        partidos_perdidos=0,
        puntos=0,
        goles_a_favor=0,
        goles_en_contra=0)

    fixture = FixtureLiga(
        id_liga=liga.id,
        id_equipo_izq=equipo_1.id_equipo,
        id_equipo_der=equipo_2.id_equipo,
        turno=1)

    repositorio = LigaRepositorio(db_test)

    repositorio.guardar_inicio_liga(liga, [tabla_1, tabla_2], [fixture])

    assert liga.estado == EstadoLiga.EN_JUEGO

    assert tabla_1 in db_test.query(TablaLiga).all()
    assert tabla_2 in db_test.query(TablaLiga).all()
    assert fixture in db_test.query(FixtureLiga).all()


def test_obtener_fixture_por_turno(db_test):
    usuario = create_usuario(db_test)
    usuario2 = create_usuario(db_test, email="pepito2@gmail.com")

    liga = crear_liga(db_test, usuario)

    equipo_1 = crear_equipo(db_test, usuario)
    equipo_2 = crear_equipo(db_test, usuario2)

    fixture = FixtureLiga(
        id_liga=liga.id,
        id_equipo_izq=equipo_1.id_equipo,
        id_equipo_der=equipo_2.id_equipo,
        turno=1)

    db_test.add(fixture)
    db_test.commit()

    repositorio = LigaRepositorio(db_test)

    resultado = repositorio.obtener_fixture_por_turno(liga.id, 1)

    assert resultado == fixture

def test_asignar_partido_fixture(db_test):
    usuario = create_usuario(db_test)
    usuario2 = create_usuario(db_test, email="pepito2@gmail.com")

    liga = crear_liga(db_test, usuario)

    equipo_1 = crear_equipo(db_test, usuario)
    equipo_2 = crear_equipo(db_test, usuario2)

    fixture = FixtureLiga(
        id_liga=liga.id,
        id_equipo_izq=equipo_1.id_equipo,
        id_equipo_der=equipo_2.id_equipo,
        turno=1)

    db_test.add(fixture)
    db_test.commit()

    repositorio = LigaRepositorio(db_test)

    resultado = repositorio.asignar_partido_fixture(fixture, 10)

    assert resultado == fixture
    assert fixture.id_partido == 10                        

def test_obtener_participante_por_equipo(db_test):
    usuario = create_usuario(db_test)

    liga = crear_liga(db_test, usuario)
    equipo = crear_equipo(db_test, usuario)

    participante = LigaParticipante(
        id_liga=liga.id,
        id_usuario=usuario.id_usuario,
        id_equipo=equipo.id_equipo,
        formacion=Formacion.DEFENSIVA)

    db_test.add(participante)
    db_test.commit()

    repositorio = LigaRepositorio(db_test)

    resultado = repositorio.obtener_participante_por_equipo(liga.id, equipo.id_equipo)

    assert resultado == participante

def test_obtener_registro_tabla(db_test):
    usuario = create_usuario(db_test)

    liga = crear_liga(db_test, usuario)
    equipo = crear_equipo(db_test, usuario)

    registro = TablaLiga(
        id_liga=liga.id,
        id_equipo=equipo.id_equipo,
        id_usuario=usuario.id_usuario,
        partidos_ganados=0,
        partidos_empatados=0,
        partidos_perdidos=0,
        puntos=0,
        goles_a_favor=0,
        goles_en_contra=0)

    db_test.add(registro)
    db_test.commit()

    repositorio = LigaRepositorio(db_test)

    resultado = repositorio.obtener_registro_tabla(liga.id, equipo.id_equipo)

    assert resultado == registro

def test_finalizar_liga(db_test):
    usuario = create_usuario(db_test)
    liga = crear_liga(db_test, usuario)

    repositorio = LigaRepositorio(db_test)

    resultado = repositorio.finalizar_liga(liga)

    assert resultado == liga
    assert resultado.estado == EstadoLiga.FINALIZADA
    