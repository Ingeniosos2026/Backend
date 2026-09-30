from unittest.mock import Mock

import pytest

from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_2_logica.errores import *
from app.capa_2_logica.servicios import Servicios, password_hash
from app.capa_2_logica.resultados import *


def test_crear_usuario_datos_invalidos():

    repositorio = Mock()
    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(DatosInvalidos):
        servicio.crear_usuario(
            email="leandro@gmail.com.ar",
            nombre="Leandro",
            id_avatar=1,
            contraseña="123456",
            nombre_club="Talleres"
        )

    repositorio.obtener_por_email.assert_not_called()
    repositorio.crear.assert_not_called()


def test_crear_usuario_nombre_vacio():

    repositorio = Mock()
    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(DatosInvalidos):
        servicio.crear_usuario(
            email="leandro@gmail.com",
            nombre="",
            id_avatar=1,
            contraseña="123456",
            nombre_club="Talleres"
        )

    repositorio.obtener_por_email.assert_not_called()
    repositorio.crear.assert_not_called()

def test_crear_usuario_contraseña_vacia():

    repositorio = Mock()
    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(DatosInvalidos):
        servicio.crear_usuario(
            email="leandro@gmail.com",
            nombre="Leandro",
            id_avatar=1,
            contraseña="",
            nombre_club="Talleres"
        )

    repositorio.obtener_por_email.assert_not_called()
    repositorio.crear.assert_not_called()

def test_crear_usuario_club_vacio():

    repositorio = Mock()
    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(DatosInvalidos):
        servicio.crear_usuario(
            email="leandro@gmail.com",
            nombre="Leandro",
            id_avatar=1,
            contraseña="123456",
            nombre_club=""
        )

    repositorio.obtener_por_email.assert_not_called()
    repositorio.crear.assert_not_called()

def test_crear_usuario_email_registrado():

    repositorio = Mock()

    usuario_existente = Usuario(
        email="leandro@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="123456",
        nombre_club="Talleres"
    )

    repositorio.obtener_por_email.return_value = usuario_existente

    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(EmailRegistrado):
        servicio.crear_usuario(
            email="leandro@gmail.com",
            nombre="Leandro",
            id_avatar=1,
            contraseña="123456",
            nombre_club="Talleres"
        )

    repositorio.obtener_por_email.assert_called_once_with("leandro@gmail.com")
    repositorio.crear.assert_not_called()


def test_crear_usuario_correctamente():

    repositorio = Mock()
    repositorio.obtener_por_email.return_value = None

    usuario_nuevo = Usuario(
        id_usuario=1,
        email="leandro@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="hash",
        nombre_club="Talleres"
    )

    repositorio.crear.return_value = usuario_nuevo
    servicio = Servicios(usuarios=repositorio)

    resultado = servicio.crear_usuario(
        email="leandro@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="123456",
        nombre_club="Talleres"
    )

    usuario = resultado.usuario

    assert usuario.id_usuario == 1
    assert usuario.email == "leandro@gmail.com"
    assert usuario.nombre == "Leandro"
    assert usuario.id_avatar == 1
    assert usuario.nombre_club == "Talleres"

    assert usuario.contraseña != "123456"
    assert usuario.contraseña is not None

    repositorio.obtener_por_email.assert_called_once_with("leandro@gmail.com")
    repositorio.crear.assert_called_once()

def test_login_usuario_correctamente():
    contraseña = "asd123"

    repositorio = Mock()
    usuario = Usuario(
        id_usuario=1,
        email="pepito@gmail.com",
        nombre="Pepitocabj",
        id_avatar=1,
        contraseña=password_hash.hash(contraseña),
        nombre_club="boca"
    )

    repositorio.obtener_por_email.return_value = usuario

    servicio = Servicios(usuarios=repositorio)

    resultado = servicio.login_usuario(
        email="pepito@gmail.com",
        contraseña=contraseña
    )

    assert resultado == usuario

    repositorio.obtener_por_email.assert_called_once_with("pepito@gmail.com")

def test_login_contraseña_incorrecta():

    repositorio = Mock()
    usuario = Usuario(
        id_usuario=1,
        email="pepito@gmail.com",
        nombre="Pepitocabj",
        id_avatar=1,
        contraseña=password_hash.hash("asd123"),
        nombre_club="boca"
    )

    repositorio.obtener_por_email.return_value = usuario

    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(CredencialesInvalidas):
        servicio.login_usuario(
            email="pepito@gmail.com",
            contraseña= "contraseña_incorrecta"
        )

def test_login_usuario_inexistente():
    repositorio = Mock()
    repositorio.obtener_por_email.return_value = None

    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(CredencialesInvalidas):
        servicio.login_usuario(
            email="inexistente@gmail.com",
            contraseña="asd123"
        )

    repositorio.obtener_por_email.assert_called_once_with(
        "inexistente@gmail.com"
    )