from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador

# helper
def create_usuario_test(db, email="pepito@gmail.com"):
    usuario = Usuario(
        email=email,
        nombre="Pepito",
        id_avatar=1,
        contraseña="asd123",
        nombre_club="Boca"
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def create_jugador_test(db, usuario_id, nombre="Messi"):
    jugador = Jugador(
        id_usuario=usuario_id,
        nombre_jugador=nombre,
        poder=60,
        agilidad=60,
        control=60,
        velocidad=60,
        fuerza=60
    )
    db.add(jugador)
    db.commit()
    db.refresh(jugador)
    return jugador

def test_crear_equipo_exitoso(client, db_test):
    usuario = create_usuario_test(db_test)
    response = client.post(f"/equipo/{usuario.id_usuario}")
    
    assert response.status_code == 201
    datos = response.json()
    assert datos["id_equipo"] is not None
    assert datos["id_usuario"] == usuario.id_usuario

def test_agregar_jugador_a_equipo_exitoso(client, db_test):
    usuario = create_usuario_test(db_test)
    equipo_response = client.post(f"/equipo/{usuario.id_usuario}")
    equipo_id = equipo_response.json()["id_equipo"]

    jugador = create_jugador_test(db_test, usuario.id_usuario)

    response = client.post(f"/equipo/{usuario.id_usuario}/{equipo_id}/jugador/{jugador.id_jugador}")
    
    assert response.status_code == 201
    datos = response.json()
    assert datos["id_equipo"] == equipo_id
    assert datos["id_jugador"] == jugador.id_jugador

def test_agregar_jugador_a_equipo_no_existente(client, db_test):
    usuario = create_usuario_test(db_test)
    jugador = create_jugador_test(db_test, usuario.id_usuario)

    id_equipo = 5892
    response = client.post(f"/equipo/{usuario.id_usuario}/{id_equipo}/jugador/{jugador.id_jugador}")
    
    assert response.status_code == 404
    assert response.json() == {
        "error": "EQUIPO_NO_ENCONTRADO",
        "mensaje": "El equipo no existe"
    }

def test_crear_equipo_usuario_no_existente(client):
    usuario_id = 5892
    response = client.post(f"/equipo/{usuario_id}")
    
    assert response.status_code == 404
    assert response.json() == {
        "error": "USUARIO_NO_ENCONTRADO",
        "mensaje": "El usuario no existe"
    }

def test_agregar_jugador_no_existente_a_equipo(client, db_test):
    usuario = create_usuario_test(db_test)
    equipo_response = client.post(f"/equipo/{usuario.id_usuario}")
    equipo_id = equipo_response.json()["id_equipo"]

    id_jugador = 5892
    response = client.post(f"/equipo/{usuario.id_usuario}/{equipo_id}/jugador/{id_jugador}")
    
    assert response.status_code == 404
    assert response.json() == {
        "error": "JUGADOR_NO_ENCONTRADO",
        "mensaje": "El jugador no existe"
    }