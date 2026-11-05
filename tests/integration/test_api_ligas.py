from unittest.mock import AsyncMock, Mock

from app.capa_0_definicion_bd.models.liga_modelos import EstadoLiga, Liga
from app.capa_0_definicion_bd.models.liga_participantes_modelos import LigaParticipante
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento
from app.capa_0_definicion_bd.models.equipos_jugadores_modelos import EquipoJugador, EstadoJugador
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.fixture_liga_modelos import FixtureLiga
from app.capa_0_definicion_bd.models.tabla_liga_modelos import TablaLiga
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones


def test_endpoint_listar_ligas_disponibles(client, db_test):
    usuario = Usuario(
        email="pepito@gmail.com",
        nombre="Pepito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="Boca")
    db_test.add(usuario)
    db_test.commit()
    db_test.refresh(usuario)

    liga_disponible = Liga(
        id_usuario=usuario.id_usuario,
        nombre="Liga publica",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=3,
        max_jugadores=10,
        duracion_partido=10)
    liga_privada = Liga(
        id_usuario=usuario.id_usuario,
        nombre="Liga privada",
        contraseña="asd",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=4,
        max_jugadores=8,
        duracion_partido=15)
    liga_en_juego = Liga(
        id_usuario=usuario.id_usuario,
        nombre="Liga en juego",
        estado=EstadoLiga.EN_JUEGO,
        min_jugadores=3,
        max_jugadores=10,
        duracion_partido=10)
    db_test.add_all([liga_disponible, liga_privada, liga_en_juego])
    db_test.commit()

    response = client.get("/ligas")

    assert response.status_code == 200
    ligas_por_nombre = {liga["nombre"]: liga for liga in response.json()}
    assert ligas_por_nombre == {
        "Liga publica": {
            "id_liga": liga_disponible.id,
            "id_usuario": usuario.id_usuario,
            "nombre": "Liga publica",
            "estado": EstadoLiga.DISPONIBLE.value,
            "min_jugadores": 3,
            "max_jugadores": 10,
            "duracion_partido": 10,
            "es_privada": False,
        },
        "Liga privada": {
            "id_liga": liga_privada.id,
            "id_usuario": usuario.id_usuario,
            "nombre": "Liga privada",
            "estado": EstadoLiga.DISPONIBLE.value,
            "min_jugadores": 4,
            "max_jugadores": 8,
            "duracion_partido": 15,
            "es_privada": True,
        },
    }
    assert "contraseña" not in response.text


def test_endpoint_listar_ligas_sin_ligas_disponibles(client):
    response = client.get("/ligas")

    assert response.status_code == 200
    assert response.json() == []

def test_iniciar_liga(client, db_test, monkeypatch):
    u1 = Usuario(
        email="jere@gmail.com",
        nombre="jerito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="belgrano")

    u2 = Usuario(
        email="tomas@gmail.com",
        nombre="toma",
        id_avatar=2,
        contraseña="asd123",
        nombre_club="talleres")

    db_test.add_all([u1, u2])
    db_test.commit()

    equipo_creador = Equipo(id_usuario=u1.id_usuario)
    equipo_participante = Equipo(id_usuario=u2.id_usuario)

    db_test.add_all([equipo_creador, equipo_participante])
    db_test.commit()
    db_test.refresh(equipo_creador)
    db_test.refresh(equipo_participante)

    liga = Liga(
        id_usuario=u1.id_usuario,
        nombre="Chiqui League",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=2,
        max_jugadores=5,
        duracion_partido=10)

    db_test.add(liga)
    db_test.commit()
    db_test.refresh(liga)

    participante_creador = LigaParticipante(
        id_liga=liga.id,
        id_usuario=u1.id_usuario,
        id_equipo=equipo_creador.id_equipo,
        formacion=Formacion.C)

    participante_usuario = LigaParticipante(
        id_liga=liga.id,
        id_usuario=u2.id_usuario,
        id_equipo=equipo_participante.id_equipo,
        formacion=Formacion.C)

    db_test.add_all([participante_creador, participante_usuario])
    db_test.commit()

    estado = Mock()
    motor = Mock()
    ejecutor = Mock()

    ejecutar = Mock()
    ejecutor.ejecutar = ejecutar

    monkeypatch.setattr("app.capa_3_api.routers.ligas.crear_estado_partido", Mock(return_value=estado))

    monkeypatch.setattr("app.capa_3_api.routers.ligas.MotorPartido", Mock(return_value=motor))

    monkeypatch.setattr("app.capa_3_api.routers.ligas.EjecutorLiga", Mock(return_value=ejecutor))

    agregar_mock = Mock()
    monkeypatch.setattr("app.capa_3_api.routers.ligas.administrador_partidas.agregar", agregar_mock)

    create_task = Mock()
    monkeypatch.setattr("app.capa_3_api.routers.ligas.asyncio.create_task", create_task)

    emitir_lobby = AsyncMock()
    monkeypatch.setattr(admin_conexiones, "emitir_lobby_liga", emitir_lobby)

    response = client.put(f"/liga/{liga.id}/{u1.id_usuario}")

    assert response.status_code == 200

    datos = response.json()

    assert datos["mensaje"] == "Liga iniciada"
    assert datos["id_liga"] == liga.id
    assert datos["id_partido"] is not None

    assert agregar_mock.call_count == 1
    create_task.assert_called_once()
    emitir_lobby.assert_awaited_once()
    assert liga.estado == EstadoLiga.EN_JUEGO


def test_iniciar_liga_no_permitido(client, db_test):
    u1 = Usuario(
        email="jere@gmail.com",
        nombre="jerito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="belgrano")

    u2 = Usuario(
        email="tomas@gmail.com",
        nombre="toma",
        id_avatar=2,
        contraseña="asd123",
        nombre_club="talleres")

    db_test.add_all([u1, u2])
    db_test.commit()

    liga = Liga(
        id_usuario=u1.id_usuario,
        nombre="Chiqui League",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=2,
        max_jugadores=5,
        duracion_partido=10)

    db_test.add(liga)
    db_test.commit()
    db_test.refresh(liga)

    response = client.put(f"/liga/{liga.id}/{u2.id_usuario}")

    assert response.status_code == 403
    assert response.json()["error"] == "INICIAR_NO_PERMITIDO"
    assert liga.estado == EstadoLiga.DISPONIBLE

def test_iniciar_liga_no_existente(client, db_test):
    u1 = Usuario(
        email="jere@gmail.com",
        nombre="jerito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="belgrano")

    db_test.add(u1)
    db_test.commit()
    db_test.refresh(u1)

    response = client.put(f"/liga/999/{u1.id_usuario}")

    assert response.status_code == 404
    assert response.json()["error"] == "LIGA_NO_ENCONTRADA"

def test_endpoint_obtener_fixture_correctamente(client, db_test):
    usuario1 = Usuario(
        email="jere@gmail.com",
        nombre="jerito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="belgrano")

    usuario2 = Usuario(
        email="tomas@gmail.com",
        nombre="toma",
        id_avatar=2,
        contraseña="asd123",
        nombre_club="talleres")

    usuario3 = Usuario(
        email="juan@gmail.com",
        nombre="juan",
        id_avatar=3,
        contraseña="asd123",
        nombre_club="instituto")

    usuario4 = Usuario(
        email="pedro@gmail.com",
        nombre="pedro",
        id_avatar=4,
        contraseña="asd123",
        nombre_club="river")

    db_test.add_all([usuario1, usuario2, usuario3, usuario4])
    db_test.commit()

    equipo1 = Equipo(id_usuario=usuario1.id_usuario)
    equipo2 = Equipo(id_usuario=usuario2.id_usuario)
    equipo3 = Equipo(id_usuario=usuario3.id_usuario)
    equipo4 = Equipo(id_usuario=usuario4.id_usuario)

    db_test.add_all([equipo1, equipo2, equipo3, equipo4])
    db_test.commit()

    db_test.refresh(equipo1)
    db_test.refresh(equipo2)
    db_test.refresh(equipo3)
    db_test.refresh(equipo4)

    liga = Liga(
        id_usuario=usuario1.id_usuario,
        nombre="Liga 123",
        estado=EstadoLiga.EN_JUEGO,
        min_jugadores=2,
        max_jugadores=10,
        duracion_partido=10)

    db_test.add(liga)
    db_test.commit()
    db_test.refresh(liga)

    fixture1 = FixtureLiga(
        id_liga=liga.id,
        id_equipo_izq=equipo1.id_equipo,
        id_equipo_der=equipo2.id_equipo,
        turno=1)

    fixture2 = FixtureLiga(
        id_liga=liga.id,
        id_equipo_izq=equipo3.id_equipo,
        id_equipo_der=equipo4.id_equipo,
        turno=2)

    db_test.add_all([fixture1, fixture2])
    db_test.commit()

    response = client.get(f"/liga/{liga.id}/fixture")

    assert response.status_code == 200

    datos = response.json()

    assert "fixture" in datos
    assert len(datos["fixture"]) == 2

    assert datos["fixture"][0]["turno"] == 1
    assert datos["fixture"][0]["equipo_izq"]["id_equipo"] == equipo1.id_equipo
    assert datos["fixture"][0]["equipo_izq"]["nombre_club"] == "belgrano"
    assert datos["fixture"][0]["equipo_der"]["id_equipo"] == equipo2.id_equipo
    assert datos["fixture"][0]["equipo_der"]["nombre_club"] == "talleres"

    assert datos["fixture"][1]["turno"] == 2
    assert datos["fixture"][1]["equipo_izq"]["id_equipo"] == equipo3.id_equipo
    assert datos["fixture"][1]["equipo_izq"]["nombre_club"] == "instituto"
    assert datos["fixture"][1]["equipo_der"]["id_equipo"] == equipo4.id_equipo
    assert datos["fixture"][1]["equipo_der"]["nombre_club"] == "river"

def test_endpoint_obtener_fixture_liga_no_existente(client):
    response = client.get("/liga/111/fixture")
    assert response.status_code == 404
    datos = response.json()

    assert datos["error"] == "LIGA_NO_ENCONTRADA"
    assert datos["mensaje"] == "La liga no existe"

def test_endpoint_obtener_fixture_liga_no_disponible(client, db_test):
    usuario = Usuario(
        email="jere@gmail.com",
        nombre="jerito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="belgrano")


    db_test.add(usuario)
    db_test.commit()
    db_test.refresh(usuario)

    liga = Liga(
        id_usuario=usuario.id_usuario,
        nombre="Liga publica",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=2,
        max_jugadores=10,
        duracion_partido=10)

    db_test.add(liga)
    db_test.commit()
    db_test.refresh(liga)

    response = client.get(f"/liga/{liga.id}/fixture")
    assert response.status_code == 409
    datos = response.json()
    assert datos["error"] == "LIGA_NO_DISPONIBLE"
    assert datos["mensaje"] == "La liga esta finalizada o no esta iniciada"

def test_endpoint_obtener_tabla_correctamente(client, db_test):
    usuario1 = Usuario(
        email="jere@gmail.com",
        nombre="jerito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="belgrano")

    usuario2 = Usuario(
        email="tomas@gmail.com",
        nombre="toma",
        id_avatar=2,
        contraseña="asd123",
        nombre_club="talleres")

    db_test.add_all([usuario1, usuario2])
    db_test.commit()

    equipo1 = Equipo(id_usuario=usuario1.id_usuario)
    equipo2 = Equipo(id_usuario=usuario2.id_usuario)

    db_test.add_all([equipo1, equipo2])
    db_test.commit()

    db_test.refresh(equipo1)
    db_test.refresh(equipo2)

    liga = Liga(
        id_usuario=usuario1.id_usuario,
        nombre="Liga 123",
        estado=EstadoLiga.EN_JUEGO,
        min_jugadores=2,
        max_jugadores=10,
        duracion_partido=10)

    db_test.add(liga)
    db_test.commit()
    db_test.refresh(liga)

    tabla1 = TablaLiga(
        id_liga=liga.id,
        id_equipo=equipo1.id_equipo,
        id_usuario=usuario1.id_usuario,
        partidos_ganados=2,
        partidos_empatados=0,
        partidos_perdidos=0,
        puntos=6,
        goles_a_favor=5,
        goles_en_contra=1)

    tabla2 = TablaLiga(
        id_liga=liga.id,
        id_equipo=equipo2.id_equipo,
        id_usuario=usuario2.id_usuario,
        partidos_ganados=0,
        partidos_empatados=0,
        partidos_perdidos=2,
        puntos=0,
        goles_a_favor=1,
        goles_en_contra=5)

    db_test.add_all([tabla1, tabla2])
    db_test.commit()

    response = client.get(f"/liga/{liga.id}/tabla")

    assert response.status_code == 200

    datos = response.json()

    assert "tabla" in datos
    assert len(datos["tabla"]) == 2
    assert datos["tabla"][0]["id_equipo"] == equipo1.id_equipo
    assert datos["tabla"][0]["puntos"] == 6
    assert datos["tabla"][0]["partidos_ganados"] == 2
    assert datos["tabla"][0]["goles_a_favor"] == 5

    assert datos["tabla"][1]["id_equipo"] == equipo2.id_equipo
    assert datos["tabla"][1]["puntos"] == 0
    assert datos["tabla"][1]["partidos_perdidos"] == 2
    assert datos["tabla"][1]["goles_en_contra"] == 5

def test_endpoint_obtener_tabla_liga_no_existente(client):
    response = client.get("/liga/111/tabla")
    assert response.status_code == 404
    datos = response.json()

    assert datos["error"] == "LIGA_NO_ENCONTRADA"
    assert datos["mensaje"] == "La liga no existe"

def test_endpoint_obtener_tabla_liga_no_disponible(client, db_test):
    usuario = Usuario(
        email="jere@gmail.com",
        nombre="jerito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="belgrano")

    db_test.add(usuario)
    db_test.commit()
    db_test.refresh(usuario)

    liga = Liga(
        id_usuario=usuario.id_usuario,
        nombre="Liga publica",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=2,
        max_jugadores=10,
        duracion_partido=10)

    db_test.add(liga)
    db_test.commit()
    db_test.refresh(liga)

    response = client.get(f"/liga/{liga.id}/tabla")

    assert response.status_code == 409
    datos = response.json()
    assert datos["error"] == "LIGA_NO_DISPONIBLE"
    assert datos["mensaje"] == "La liga esta finalizada o no esta iniciada"

def test_endpoint_obtener_equipo_de_liga(client, db_test):
    usuario = Usuario(
        email="Pepito@gmail.com",
        nombre="Pepito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="Boca",
    )
    db_test.add(usuario)
    db_test.commit()

    equipo = Equipo(id_usuario=usuario.id_usuario)
    liga = Liga(
        id_usuario=usuario.id_usuario,
        nombre="superliga",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=2,
        max_jugadores=10,
        duracion_partido=10,
    )
    jugador = Jugador(
        id_usuario=usuario.id_usuario,
        nombre_jugador="Messi",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60,
    )
    suplente = Jugador(
        id_usuario=usuario.id_usuario,
        nombre_jugador="Paredes",
        control=60,
        agilidad=60,
        fuerza=60,
        poder=60,
        velocidad=60,
    )
    comportamiento = Comportamiento(id_usuario=usuario.id_usuario, nombre="Atacar", codigo="")
    db_test.add_all([equipo, liga, jugador, suplente, comportamiento])
    db_test.commit()

    participacion = LigaParticipante(
        id_liga=liga.id,
        id_usuario=usuario.id_usuario,
        id_equipo=equipo.id_equipo,
        formacion=Formacion.DEFENSIVA,
    )
    asociacion = EquipoJugador(
        id_equipo=equipo.id_equipo,
        id_jugador=jugador.id_jugador,
        id_comportamiento=comportamiento.id,
        estado=EstadoJugador.TITULAR,
    )
    asociacion_suplente = EquipoJugador(
        id_equipo=equipo.id_equipo,
        id_jugador=suplente.id_jugador,
        estado=EstadoJugador.SUPLENTE,
    )
    db_test.add_all([participacion, asociacion, asociacion_suplente])
    db_test.commit()

    response = client.get(f"/liga/{liga.id}/equipo/{equipo.id_equipo}")

    assert response.status_code == 200
    assert response.json() == {
        "id_equipo": equipo.id_equipo,
        "formacion": "defensiva",
        "jugadores": [
            {
                "id": jugador.id_jugador,
                "nombre": "Messi",
                "estado": "titular",
                "comportamiento": {
                    "id": comportamiento.id,
                    "nombre": "Atacar",
                },
            },
            {
                "id": suplente.id_jugador,
                "nombre": "Paredes",
                "estado": "suplente",
                "comportamiento": None,
            },
        ],
    }


def test_endpoint_obtener_equipo_de_liga_rechaza_equipo_que_no_participa(client, db_test):
    usuario = Usuario(
        email="Pepito@gmail.com",
        nombre="Pepito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="Boca",
    )
    db_test.add(usuario)
    db_test.commit()
    equipo = Equipo(id_usuario=usuario.id_usuario)
    liga = Liga(
        id_usuario=usuario.id_usuario,
        nombre="premier",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=2,
        max_jugadores=10,
        duracion_partido=10,
    )
    db_test.add_all([equipo, liga])
    db_test.commit()

    response = client.get(f"/liga/{liga.id}/equipo/{equipo.id_equipo}")

    assert response.status_code == 404
    assert response.json()["error"] == "EQUIPO_NO_ENCONTRADO"


def test_endpoint_obtener_equipo_de_liga_rechaza_liga_inexistente(client):
    response = client.get("/liga/999/equipo/1")

    assert response.status_code == 404
    assert response.json()["error"] == "LIGA_NO_ENCONTRADA"