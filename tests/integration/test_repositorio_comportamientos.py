
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento as ComportamientoModelo
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario 
from app.capa_1_acceso_datos.repositorios.comportamientos import ComportamientoRepositorio


def create_usuario(session):
    usuario = Usuario(
        email="famaf.ingeniosos@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="Ingenieria-la-mejor-materia",
        nombre_club="Talleres"
    )

    session.add(usuario)
    session.commit()

    return usuario

def test_obtener_comportamientos_usuario(db_test):

    Usuario_1 = create_usuario(db_test)
    comportamiento_1 = ComportamientoModelo(
        id_usuario=1,
        nombre="Defender",
        codigo="codigo defender"
    )

    comportamiento_2 = ComportamientoModelo(
        id_usuario=1,
        nombre="Atacar",
        codigo="codigo atacar"
    )

    comportamiento_3 = ComportamientoModelo(
        id_usuario=1,
        nombre="Pasar",
        codigo="codigo pasar"
    )

    db_test.add_all([comportamiento_1, comportamiento_2, comportamiento_3])
    db_test.commit()

    repositorio = ComportamientoRepositorio(db_test)

    resultado = repositorio.obtener_comportamientos_usuario(1)

    assert len(resultado) == 3
    assert comportamiento_1 in resultado
    assert comportamiento_2 in resultado
    assert comportamiento_3 in resultado


