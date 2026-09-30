from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_1_acceso_datos.repositorios.usuarios import UsuarioRepositorio



def test_crear_usuario(db_test):

    repositorio = UsuarioRepositorio(db_test)

    usuario = Usuario(
        email="famaf.ingeniosos@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="Ingenieria-la-mejor-materia",
        nombre_club="Talleres"
    )

    resultado = repositorio.crear(usuario)

    assert resultado.id_usuario is not None
    assert resultado.email == "famaf.ingeniosos@gmail.com"
    assert resultado.nombre == "Leandro"
    assert resultado.id_avatar == 1
    assert resultado.nombre_club == "Talleres"


def test_obtener_usuario_por_email(db_test):

    repositorio = UsuarioRepositorio(db_test)

    usuario = Usuario(
        email="famaf.ingeniosos@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="Ingenieria-la-mejor-materia",
        nombre_club="Talleres"
    )

    repositorio.crear(usuario)

    resultado = repositorio.obtener_por_email("famaf.ingeniosos@gmail.com")

    assert resultado is not None
    assert resultado.email == "famaf.ingeniosos@gmail.com"
    assert resultado.nombre == "Leandro"


def test_obtener_usuario_por_email_inexistente(db_test):

    repositorio = UsuarioRepositorio(db_test)

    resultado = repositorio.obtener_por_email("telacreiste@gmail.com")

    assert resultado is None