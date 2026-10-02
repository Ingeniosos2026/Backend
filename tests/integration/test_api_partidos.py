from app.capa_0_definicion_bd.models.equipo_modelos import Equipo

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

    equipo = Equipo(id_usuario=usuario_id)
    db_test.add(equipo)
    db_test.commit()
    db_test.refresh(equipo)

    response = client.post(f"/partido/{usuario_id}", json={
        "id_equipo": equipo.id_equipo,
        "duracion": 5
    })
    assert response.status_code == 201
    datos = response.json()
    assert datos["id_partido"] is not None
    assert datos["id_usuario_1"] == usuario_id
    assert datos["id_equipo_1"] == equipo.id_equipo
    assert datos["duracion"] == 5
    assert datos["tipo"] == "AMISTOSO"
    assert datos["estado"] == "DISPONIBLE"

def test_crear_amistoso_equipo_no_existente(client):
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
        "id_equipo": 999,
        "duracion": 5
    })
    assert response.status_code == 404
    assert response.json() == {
        "error": "EQUIPO_NO_ENCONTRADO",
        "mensaje": "El equipo no existe"
    }

def test_crear_amistoso_duracion_invalida(client, db_test):
    usuario = client.post("/usuario", json={
        "email": "pepito@gmail.com",
        "nombre": "Pepito",
        "avatar": 1,
        "contraseña": "asd123",
        "club": "Boca"
    })
    assert usuario.status_code == 201
    usuario_id = usuario.json()['id']

    equipo = Equipo(id_usuario=usuario_id)
    db_test.add(equipo)
    db_test.commit()
    db_test.refresh(equipo)

    response = client.post(f"/partido/{usuario_id}", json={
        "id_equipo": equipo.id_equipo,
        "duracion": 0
    })
    assert response.status_code == 400
    assert response.json() == {
        "error": "DATOS_INVALIDOS",
        "mensaje": "La duracion del partido debe ser mayor a 0"
    }