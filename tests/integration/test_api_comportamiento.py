import pytest
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento

def create_datos_prueba(db):
    usuario = Usuario(
        email="test_comportamiento@gmail.com",
        nombre="Tomas",
        id_avatar=1,
        contraseña="hola123",
        nombre_club="Talleres",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    comp = Comportamiento(
        id_usuario=usuario.id_usuario,
        nombre="Arquero",
        codigo= "Correr(centro_arco)"
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)

    return usuario, comp

def test_endpoint_ver_comportamiento_exitoso(client, db_test):
    usuario, comp = create_datos_prueba(db_test)
    response = client.get(f"/comportamiento/{usuario.id_usuario}/{comp.id}")
    
    assert response.status_code == 200
    datos = response.json()
    assert datos["id"] == comp.id
    assert datos["nombre"] == "Arquero"
    assert "Correr(centro_arco)" in datos["codigo"]

def test_endpoint_ver_comportamiento_no_eixste(client, db_test):
    usuario, _ = create_datos_prueba(db_test)
    response = client.get(f"/comportamiento/{usuario.id_usuario}/999")
    
    assert response.status_code == 404
    assert response.json() == {
        "error": "COMPORTAMIENTO_NO_ENCONTRADO",
        "mensaje": "No existe el comportamiento"
    }


def create_datos_prueba_listar(db):
    usuario = Usuario(
        email="famaf.ingeniosos@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="Ingenieria-la-mejor-materia",
        nombre_club="Talleres")

    db.add(usuario)
    db.commit()

    comp1 = Comportamiento(
        id_usuario=1,
        nombre="Defender",
        codigo="codigo defender")

    comp2 = Comportamiento(
        id_usuario=1,
        nombre="Atacar",
        codigo="codigo atacar")

    db.add_all([comp1, comp2])
    db.commit()

    return usuario, comp1, comp2


def test_endpoint_listar_comportamientos_exitoso(client, db_test):
    usuario, comp1, comp2 = create_datos_prueba_listar(db_test)

    response = client.get(f"/comportamientos/{usuario.id_usuario}")

    assert response.status_code == 200

    datos = response.json()

    assert len(datos) == 2
    assert datos[0]["id"] == comp1.id
    assert datos[0]["nombre"] == "Defender"
    assert datos[0]["codigo"] == "codigo defender"

    assert datos[1]["id"] == comp2.id
    assert datos[1]["nombre"] == "Atacar"
    assert datos[1]["codigo"] == "codigo atacar"


def test_endpoint_listar_comportamientos_no_existentes(client, db_test):

    tomas = Usuario(
        email="test_comportamiento@gmail.com",
        nombre="Tomas",
        id_avatar=1,
        contraseña="hola123",
        nombre_club="Talleres",
    )

    db_test.add(tomas)
    db_test.commit()

    response = client.get(f"/comportamientos/{tomas.id_usuario}")

    assert response.status_code == 404
    assert response.json() == {"error": "COMPORTAMIENTOS_NO_ENCONTRADOS", "mensaje": "No hay comportamientos disponibles"}
