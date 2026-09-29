
def test_crear_usuario(client):

    response = client.post("/usuario",
        json={
            "email": "famaf.ingeniosos@gmail.com",
            "nombre": "Leandro",
            "id_avatar": 1,
            "contraseña": "Ingenieria-la-mejor-materia",
            "nombre_club": "Talleres",
        }
    )

    assert response.status_code == 201

    datos = response.json()

    assert datos["mensaje"] == "Usuario creado"
    assert datos["id_usuario"] is not None
    assert datos["email"] == "famaf.ingeniosos@gmail.com"
    assert datos["nombre"] == "Leandro"
    assert datos["id_avatar"] == 1
    assert datos["nombre_club"] == "Talleres"

    assert "contraseña" not in datos


def test_crear_usuario_email_invalido(client):

    response = client.post("/usuario",
        json={
            "email": "famaf.ingeniosos@gmail.com.ar",
            "nombre": "Leandro",
            "id_avatar": 1,
            "contraseña": "Ingenieria-la-mejor-materia",
            "nombre_club": "Talleres"
        }
    )

    assert response.status_code == 400

    assert response.json() == {"detail": "El email no es válido"}


def test_crear_usuario_email_registrado(client):

    datos = {
        "email": "famaf.ingeniosos@gmail.com",
        "nombre": "Leandro",
        "id_avatar": 1,
        "contraseña": "Ingenieria-la-mejor-materia",
        "nombre_club": "Talleres"
    }

    primera_respuesta = client.post("/usuario", json=datos)

    assert primera_respuesta.status_code == 201

    segunda_respuesta = client.post("/usuario", json=datos)

    assert segunda_respuesta.status_code == 400

    assert segunda_respuesta.json() == {"detail": "El email ya está registrado"}