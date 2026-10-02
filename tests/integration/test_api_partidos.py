from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo

# helper
def crear_jugadores_test(db_test, usuario_id, cantidad=6):
    jugadores = [
        Jugador(
            id_usuario=usuario_id,
            nombre_jugador=f"Jugador {numero}",
            poder=60,
            agilidad=60,
            control=60,
            velocidad=60,
            fuerza=60,
        )
        for numero in range(cantidad)
    ]
    db_test.add_all(jugadores)
    db_test.commit()
    return jugadores




def test_crear_amistoso(client, db_test):
    usuario = client.post("/usuario", json={
        "email": "pepito@gmail.com",
        "nombre": "Pepito",
        "avatar": 1,
        "contraseña": "asd123",
        "club": "Boca"
    })

    assert usuario.status_code == 201
    usuario_id = usuario.json()['id']
    jugadores = crear_jugadores_test(db_test, usuario_id)

    response = client.post(f"/partido/{usuario_id}", json={
        "jugadores": [jugador.id_jugador for jugador in jugadores],
        "duracion": 5,
        "formacion": 1,
    })
    assert response.status_code == 201
    datos = response.json()
    assert datos["id_partido"] is not None
    assert datos["id_usuario_1"] == usuario_id
    assert datos["id_equipo_1"] is not None
    assert datos["duracion"] == 5
    assert datos["formacion"] == 1
    assert datos["tipo"] == "AMISTOSO"
    assert datos["estado"] == "DISPONIBLE"
    equipo = db_test.get(Equipo, datos["id_equipo_1"])
    assert equipo.id_usuario == usuario_id
    assert len(equipo.jugadores_amistosos) == 6

def test_crear_amistoso_jugador_no_existente(client):
    usuario = client.post("/usuario", json={
        "email": "pepito@gmail.com",
        "nombre": "Pepito",
        "avatar": 1,
        "contraseña": "asd123",
        "club": "Boca"
    })
    assert usuario.status_code == 201
    usuario_id = usuario.json()['id']

    response = client.post(f"/partido/{usuario_id}", json={
        "jugadores": [999, 1000, 1001, 1002, 1003, 1004],
        "duracion": 5,
        "formacion": 1,
    })
    assert response.status_code == 404
    assert response.json() == {
        "error": "JUGADOR_NO_ENCONTRADO",
        "mensaje": "El jugador no existe o no pertenece al usuario"
    }

def test_crear_amistoso_duracion_invalida(client):
    usuario = client.post("/usuario", json={
        "email": "pepito@gmail.com",
        "nombre": "Pepito",
        "avatar": 1,
        "contraseña": "asd123",
        "club": "Boca"
    })
    assert usuario.status_code == 201
    usuario_id = usuario.json()['id']

    response = client.post(f"/partido/{usuario_id}", json={
        "jugadores": [1, 2, 3, 4, 5, 6],
        "duracion": 0,
        "formacion": 1,
    })
    assert response.status_code == 400
    assert response.json() == {
        "error": "DATOS_INVALIDOS",
        "mensaje": "La duracion del partido debe ser mayor a 0 y se deben seleccionar 6 jugadores distintos"
    }

def test_crear_amistoso_formacion_invalida(client):
    usuario = client.post("/usuario", json={
        "email": "pepito@gmail.com",
        "nombre": "Pepito",
        "avatar": 1,
        "contraseña": "asd123",
        "club": "Boca"
    })
    usuario_id = usuario.json()["id"]

    response = client.post(f"/partido/{usuario_id}", json={
        "jugadores": [1, 2, 3, 4, 5, 6],
        "duracion": 5,
        "formacion": 5,
    })

    assert response.status_code == 422