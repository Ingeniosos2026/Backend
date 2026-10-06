import pytest
from sqlalchemy.exc import IntegrityError

from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento


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


def test_crear_comportamiento(db_test):
    usuario = create_usuario(db_test)

    comportamiento = Comportamiento(
        id_usuario=usuario.id_usuario,
        nombre="Defensa básica",
        codigo="def comportamiento(jugador): pass",
    )

    db_test.add(comportamiento)
    db_test.commit()

    assert comportamiento.id is not None
    assert comportamiento.id_usuario == usuario.id_usuario

def test_usuario_multiple_comportamientos(db_test):
    usuario = create_usuario(db_test)

    comportamiento_1 = Comportamiento(
        id_usuario=usuario.id_usuario,
        nombre="Defensa",
        codigo="codigo defensa",
    )

    comportamiento_2 = Comportamiento(
        id_usuario=usuario.id_usuario,
        nombre="Ataque",
        codigo="codigo ataque",
    )

    db_test.add_all([
        comportamiento_1,
        comportamiento_2,
    ])

    db_test.commit()

    db_test.refresh(usuario)

    assert len(usuario.comportamientos) == 2
    assert comportamiento_1 in usuario.comportamientos
    assert comportamiento_2 in usuario.comportamientos

def test_comportamiento_requiere_usuario_existente(db_test):

    comportamiento = Comportamiento(
        id_usuario=999,
        nombre="Comportamiento inválido",
        codigo="codigo",
    )

    db_test.add(comportamiento)

    with pytest.raises(IntegrityError):
        db_test.commit()