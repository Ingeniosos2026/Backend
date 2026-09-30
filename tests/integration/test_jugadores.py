import pytest
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador


def create_usuario_aux(session):
    usuario = Usuario(
        email="test_jugador@example.com",
        nombre="Tomas",
        id_avatar=1,
        contraseña="hola123",
        nombre_club="Talleres",
    )
    session.add(usuario)
    session.commit()
    return usuario

def test_crear_jugador_exitoso(db_test):
    usuario = create_usuario_aux(db_test)

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

    assert jugador.id_jugador is not None
    assert jugador.id_usuario == usuario.id_usuario