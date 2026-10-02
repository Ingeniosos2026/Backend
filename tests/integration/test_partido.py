import pytest
from sqlalchemy.exc import IntegrityError
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.partidos_modelos import Partido, TipoPartido, EstadoPartido

def crear_escenario_partido(db_test):
    usuario_1 = Usuario(
        email="tomas@gmail.com",
        nombre="Tomas",
        id_avatar=1,
        contraseña="hola123",
        nombre_club="Talleres",
    )
    usuario_2 = Usuario(
        email="pepito@gmail.com",
        nombre="pepitox",
        id_avatar=2,
        contraseña="123",
        nombre_club="pepito fc"
    )
    db_test.add_all([usuario_1, usuario_2])
    db_test.commit()

    equipo_1 = Equipo(id_usuario=usuario_1.id_usuario)
    equipo_2 = Equipo(id_usuario=usuario_2.id_usuario)
    
    db_test.add_all([equipo_1, equipo_2])
    db_test.commit()

    return usuario_1, usuario_2, equipo_1, equipo_2


def test_crear_partido_exitoso(db_test):
    u1, u2, e1, e2 = crear_escenario_partido(db_test)

    partido = Partido(
        id_usuario_1=u1.id_usuario,
        id_usuario_2=u2.id_usuario,
        id_equipo_1=e1.id_equipo,
        id_equipo_2=e2.id_equipo,
        duracion_partido=10,
        tipo_partido=TipoPartido.AMISTOSO,
        estado_partido=EstadoPartido.PENDIENTE
    )

    db_test.add(partido)
    db_test.commit()
    db_test.refresh(partido)

    assert partido.id_partido is not None
    assert partido.id_usuario_1 == u1.id_usuario
    assert partido.id_usuario_2 == u2.id_usuario
    assert partido.id_equipo_1 == e1.id_equipo
    assert partido.id_equipo_2 == e2.id_equipo
    assert partido.duracion_partido == 10
    assert partido.tipo_partido == TipoPartido.AMISTOSO
    assert partido.estado_partido == EstadoPartido.PENDIENTE

