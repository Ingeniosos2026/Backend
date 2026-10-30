from app.capa_0_definicion_bd.models.liga_modelos import EstadoLiga, Liga
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario


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
