import pytest

from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import CredencialesInvalidas
from app.capa_1_acceso_datos.repositorios.usuarios import UsuarioRepositorio

def test_login_usuario_correcto(db_test):
    repo = UsuarioRepositorio(db_test)
    servicio = Servicios(usuarios=repo)

    servicio.crear_usuario(
        email="pepito@gmail.com",
        nombre="pepitocabj",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="boca"
    )

    usuario = servicio.login_usuario(
        email="pepito@gmail.com",
        contraseña="asd123"
    )

    assert usuario.email == "pepito@gmail.com"

def test_login_contraseña_incorrecta(db_test):
    repo = UsuarioRepositorio(db_test)
    servicio = Servicios(usuarios=repo)

    servicio.crear_usuario(
        email="pepito@gmail.com",
        nombre="pepitocabj",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="boca"
    )

    with pytest.raises(CredencialesInvalidas):
        servicio.login_usuario(
            email="pepito@gmail.com",
            contraseña="contraseña_incorrecta"
        )

def test_login_usuario_inexistente(db_test):
    repo = UsuarioRepositorio(db_test)
    servicio = Servicios(usuarios=repo)

    with pytest.raises(CredencialesInvalidas):
        servicio.login_usuario(
            email="noexiste@gmail.com",
            contraseña="password123"
        )

def test_contraseña_se_guarda_hasheada(db_test):
    repo = UsuarioRepositorio(db_test)
    servicio = Servicios(usuarios=repo)

    servicio.crear_usuario(
        email="pepito@gmail.com",
        nombre="pepitocabj",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="boca"
    )

    usuario = repo.obtener_por_email("pepito@gmail.com")

    assert usuario is not None
    assert usuario.contraseña != "asd123"