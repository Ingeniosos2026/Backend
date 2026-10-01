import pytest
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario

def create_usuario_test(db):
    usuario = Usuario(
        email="test_jugador@gmail.com",
        nombre="Tomas",
        id_avatar=1,
        contraseña="hola123",
        nombre_club="Talleres",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def test_endpoint_crear_jugador_exitoso(client, db_test):
    usuario = create_usuario_test(db_test)
    payload = {
        "nombre": "Messi",
        "power": 60,
        "agility": 60,
        "control": 60,
        "speed": 60,
        "strength": 60
    }

    response = client.post(f"/jugador/{usuario.id_usuario}", json=payload)
    
    assert response.status_code == 201
    datos = response.json()
    assert datos["id"] is not None
    assert datos["nombre"] == "Messi"
    assert datos["power"] == 60

def test_endpoint_rechaza_suma_distinta_a_300(client, db_test):
    usuario = create_usuario_test(db_test)
    payload = {
        "nombre": "Jugador burro",
        "power": 50,
        "agility": 50,
        "control": 50,
        "speed": 50,
        "strength": 50
    }

    response = client.post(f"/jugador/{usuario.id_usuario}", json=payload)
    
    assert response.status_code == 400
    assert response.json() == {
        "error": "DATOS_INVALIDOS",
        "mensaje": "Las estadisticas no pueden ser mayores a 100 ni menores a 20 y el total debe ser menor o igual a 300"
    }