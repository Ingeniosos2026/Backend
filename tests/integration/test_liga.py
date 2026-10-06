from sqlalchemy.exc import IntegrityError

import pytest

from app.capa_0_definicion_bd.models.liga_modelos import Liga, EstadoLiga
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario

def create_usuario(session):
    usuario = Usuario(
        email="test@example.com",
        nombre="Usuario Test",
        id_avatar=1,
        contraseña="password",
        nombre_club="Club Test",
    )

    session.add(usuario)
    session.commit()

    return usuario

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

    liga = Liga(
        id_usuario=usuario.id_usuario,
        nombre="Liga inválida",
        contraseña="1234",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=2,
        max_jugadores=10,
        duracion_partido=10,
    )

    db_test.add(liga)

    with pytest.raises(IntegrityError):
        db_test.commit()

    db_test.rollback()

def test_max_jugadores_no_puede_ser_mayor_a_10(db_test):
    usuario = create_usuario(db_test)

    liga = Liga(
        id_usuario=usuario.id_usuario,
        nombre="Liga inválida",
        contraseña="1234",
        estado=EstadoLiga.DISPONIBLE,
        min_jugadores=3,
        max_jugadores=11,
        duracion_partido=10,
    )

    db_test.add(liga)

    with pytest.raises(IntegrityError):
        db_test.commit()

    db_test.rollback()

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