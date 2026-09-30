
def test_crear_usuario(client):

    response = client.post("/usuario",
        json={
            "email": "famaf.ingeniosos@gmail.com",
            "nombre": "Leandro",
            "avatar": 1,
            "contraseña": "Ingenieria-la-mejor-materia",
            "club": "Talleres",
        }
    )

    assert response.status_code == 201

    datos = response.json()

    assert datos["mensaje"] == "Usuario creado"
    assert datos["id"] is not None
    assert datos["email"] == "famaf.ingeniosos@gmail.com"
    assert datos["nombre"] == "Leandro"
    assert datos["avatar"] == 1
    assert datos["club"] == "Talleres"

    assert "contraseña" not in datos


def test_crear_usuario_email_invalido(client):

    response = client.post("/usuario",
        json={
            "email": "famaf.ingeniosos@gmail.com.ar",
            "nombre": "Leandro",
            "avatar": 1,
            "contraseña": "Ingenieria-la-mejor-materia",
            "club": "Talleres"
        }
    )

    assert response.status_code == 400

    assert response.json() == {"error": "DATOS_INVALIDOS", "mensaje": "Los datos enviados no son válidos"}


def test_crear_usuario_email_registrado(client):

    datos = {
        "email": "famaf.ingeniosos@gmail.com",
        "nombre": "Leandro",
        "avatar": 1,
        "contraseña": "Ingenieria-la-mejor-materia",
        "club": "Talleres"
    }

    primera_respuesta = client.post("/usuario", json=datos)

    assert primera_respuesta.status_code == 201

    segunda_respuesta = client.post("/usuario", json=datos)

    assert segunda_respuesta.status_code == 409

    assert segunda_respuesta.json() == {"error": "USUARIO_YA_EXISTE", "mensaje": "Ya existe un usuario con esos datos"}