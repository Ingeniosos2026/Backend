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