from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario


def test_crear_usuario(db_test):

    usuario = Usuario(
        email="famaf.ingeniosos@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="Ingenieria-la-mejor-materia",
        nombre_club="Talleres"
    )

    db_test.add(usuario)
    db_test.commit()

    assert usuario.id_usuario is not None
    assert usuario.email == "famaf.ingeniosos@gmail.com"
    assert usuario.nombre == "Leandro"
    assert usuario.id_avatar == 1
    assert usuario.contraseña == "Ingenieria-la-mejor-materia"
    assert usuario.nombre_club == "Talleres"