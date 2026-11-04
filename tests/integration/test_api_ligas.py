from unittest.mock import AsyncMock, Mock

from app.capa_0_definicion_bd.models.liga_modelos import EstadoLiga, Liga
from app.capa_0_definicion_bd.models.liga_participantes_modelos import LigaParticipante
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
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