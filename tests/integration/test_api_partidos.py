from unittest.mock import AsyncMock, Mock
import pytest

from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.equipos_jugadores_modelos import EstadoJugador, EquipoJugador
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento
from app.capa_0_definicion_bd.models.partidos_modelos import (EstadoPartido, Formacion, TipoPartido, Partido)
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_2_logica.errores import *
from app.capa_2_logica.resultados import CrearPartidoResultado, CambioJugadorResultado
from app.capa_3_api.dependencias import obtener_servicio
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones


#helper
def crear_override_servicio(servicio):
    def obtener_servicio_de_prueba():
        return servicio

    return obtener_servicio_de_prueba



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

def preparar_jugadores_equipo_test(db_test, usuario_id, equipo_id):
    jugadores = crear_jugadores_test(db_test, usuario_id)
    comportamiento = (db_test.query(Comportamiento).filter(Comportamiento.id_usuario == usuario_id).first())
    assert comportamiento is not None

    asociaciones = [
        EquipoJugador(
            id_equipo=equipo_id,
            id_jugador=jugador.id_jugador,
            id_comportamiento=comportamiento.id,
            estado=(
                EstadoJugador.TITULAR
                if indice < 3
                else EstadoJugador.SUPLENTE))
        for indice, jugador in enumerate(jugadores)
    ]

    db_test.add_all(asociaciones)
    db_test.commit()

    return jugadores

def crear_partido_pendiente_test(client, db_test):
    usuario_1 = client.post("/usuario", json={
        "email": "lean@gmail.com",
        "nombre": "Lean",
        "avatar": 1,
        "contraseña": "asd123",
        "club": "talleres"
    })

    assert usuario_1.status_code == 201
    usuario_1_id = usuario_1.json()["id"]

    usuario_2 = client.post("/usuario", json={
        "email": "juan@gmail.com",
        "nombre": "juan",
        "avatar": 2,
        "contraseña": "juan",
        "club": "boca"
    })

    assert usuario_2.status_code == 201
    usuario_2_id = usuario_2.json()["id"]

    equipo_1 = Equipo(id_usuario=usuario_1_id) 
    equipo_2 = Equipo(id_usuario=usuario_2_id) 
    db_test.add_all([equipo_1, equipo_2]) 
    db_test.commit() 
    db_test.refresh(equipo_1) 
    db_test.refresh(equipo_2)

    equipo_1 = db_test.query(Equipo).filter(Equipo.id_usuario == usuario_1_id).first()
    equipo_2 = db_test.query(Equipo).filter(Equipo.id_usuario == usuario_2_id).first()

    partido = Partido(
        id_usuario_1=usuario_1_id,
        id_usuario_2=usuario_2_id,
        id_equipo_1=equipo_1.id_equipo,
        id_equipo_2=equipo_2.id_equipo,
        duracion_partido=5,
        formacion_1=Formacion.OFENSIVA,
        formacion_2=Formacion.DEFENSIVA,
        tipo_partido=TipoPartido.AMISTOSO,
        estado_partido=EstadoPartido.PENDIENTE)

    db_test.add(partido)
    db_test.commit()
    db_test.refresh(partido)

    return partido, usuario_1_id




def test_crear_amistoso(client, db_test, monkeypatch):
    difundir = AsyncMock()
    monkeypatch.setattr(admin_conexiones, "difundir", difundir)
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
    comportamiento = (
        db_test.query(Comportamiento)
        .filter(Comportamiento.id_usuario == usuario_id)
        .first()
    )
    assert comportamiento is not None

    response = client.post(f"/partido/{usuario_id}", json={
        "jugadores": [
            {
                "id_jugador": jugador.id_jugador,
                "id_comportamiento": comportamiento.id,
            }
            for jugador in jugadores
        ],
        "duracion": 5,
        "formacion": "ofensiva",
    })
    assert response.status_code == 201
    datos = response.json()
    assert datos["id_partido"] is not None
    assert datos["id_usuario_1"] == usuario_id
    assert datos["id_equipo_1"] is not None
    assert datos["duracion"] == 5
    assert datos["formacion_1"] == "ofensiva"
    assert datos["formacion_2"] is None
    assert datos["tipo"] == "AMISTOSO"
    assert datos["estado"] == "DISPONIBLE"
    equipo = db_test.get(Equipo, datos["id_equipo_1"])
    assert equipo.id_usuario == usuario_id
    assert len(equipo.jugadores) == 6
    assert all(asociacion.comportamiento.id == comportamiento.id for asociacion in equipo.jugadores)
    assert {jugador.id_jugador: jugador.estado for jugador in equipo.jugadores} == {
        jugador.id_jugador: (
            EstadoJugador.TITULAR if indice < 3 else EstadoJugador.SUPLENTE
        )
        for indice, jugador in enumerate(jugadores)
    }

    difundir.assert_awaited_once_with("amistoso_creado", 
            {"id_partido": datos["id_partido"], 
            "duracion": 5, 
            "tipo": "AMISTOSO", 
            "estado": "DISPONIBLE"})



@pytest.mark.parametrize(
    ("error", "status_code", "error_code"),
    [
        (DatosInvalidos, 400, "DATOS_INVALIDOS"),
        (EquipoNoEncontrado, 404, "EQUIPO_NO_ENCONTRADO"),
        (JugadorNoEncontrado, 404, "JUGADOR_NO_ENCONTRADO"),
        (ComportamientoNoEncontrado, 404, "COMPORTAMIENTO_NO_ENCONTRADO"),
        (RuntimeError, 500, "ERROR_INTERNO"),
    ],
)
def test_crear_amistoso_mapea_errores_del_servicio(client, error, status_code, error_code):
    servicio = Mock()
    servicio.crear_amistoso.side_effect = error()
    client.app.dependency_overrides[obtener_servicio] = crear_override_servicio(servicio)

    response = client.post("/partido/10", json={
        "jugadores": [
            {"id_jugador": jugador_id, "id_comportamiento": 1}
            for jugador_id in range(1, 7)
        ],
        "duracion": 5,
        "formacion": "ofensiva",
    })

    assert response.status_code == status_code
    assert response.json()["error"] == error_code


def test_unirse_amistoso_emite_evento_y_devuelve_partido(client, db_test, monkeypatch):
    emitir_lobby = AsyncMock()
    monkeypatch.setattr(admin_conexiones,"emitir_lobby", emitir_lobby)

    respuesta_owner = client.post(
        "/usuario",
        json={"email": "owner@gmail.com",
            "nombre": "Leandro",
            "avatar": 1,
            "contraseña": "asd123",
            "club": "Los Pibes FC"})

    assert respuesta_owner.status_code == 201
    owner_id = respuesta_owner.json()["id"]

    respuesta_unido = client.post(
        "/usuario",
        json={
            "email": "juan@gmail.com",
            "nombre": "Juan",
            "avatar": 2,
            "contraseña": "asd123",
            "club": "Los Cracks FC"})

    assert respuesta_unido.status_code == 201
    usuario_unido_id = respuesta_unido.json()["id"]

    jugadores_owner = crear_jugadores_test(db_test, owner_id)
    jugadores_unido = crear_jugadores_test(db_test, usuario_unido_id)
    comportamientos_owner = (db_test.query(Comportamiento).filter(Comportamiento.id_usuario == owner_id).all())
    comportamientos_unido = (db_test.query(Comportamiento).filter(Comportamiento.id_usuario == usuario_unido_id).all())

@pytest.mark.parametrize(
    ("error", "status_code", "error_code"),
    [
        (PartidoNoEncontrado, 404, "PARTIDO_NO_ENCONTRADO"),
        (PartidoNoDisponible, 409, "PARTIDO_NO_DISPONIBLE"),
        (UsuarioNoEncontrado, 404, "USUARIO_NO_ENCONTRADO"),
        (JugadoresInsuficientes, 400, "JUGADORES_INSUFICIENTES"),
        (DatosInvalidos, 400, "DATOS_INVALIDOS"),
        (JugadorNoEncontrado, 404, "JUGADOR_NO_ENCONTRADO"),
        (ComportamientoNoEncontrado, 404, "COMPORTAMIENTO_NO_ENCONTRADO"),
    ],
)
def test_unirse_amistoso_mapea_errores_y_no_emite_evento(client, monkeypatch, error, status_code, error_code):
    servicio = Mock()
    servicio.unirse_amistoso.side_effect = error()
    client.app.dependency_overrides[obtener_servicio] = crear_override_servicio(servicio)
    emitir_lobby = AsyncMock()
    monkeypatch.setattr(admin_conexiones, "emitir_lobby", emitir_lobby)

    response = client.put("/partido/51/unirse/10", json={
        "jugadores": [
            {"id_jugador": jugador_id, "id_comportamiento": 1}
            for jugador_id in range(1, 7)
        ],
        "formacion": "defensiva",
    })

    assert response.status_code == status_code
    assert response.json()["error"] == error_code
    emitir_lobby.assert_not_awaited()


def test_unirse_amistoso_rechaza_formacion_invalida(client):
    servicio = Mock()
    client.app.dependency_overrides[obtener_servicio] = crear_override_servicio(servicio)

    response = client.put("/partido/51/unirse/10", json={
        "jugadores": [
            {"id_jugador": jugador_id, "id_comportamiento": 1}
            for jugador_id in range(1, 7)
        ],
        "formacion": "todos al arco",
    })

    assert response.status_code == 422
    servicio.unirse_amistoso.assert_not_called()


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
        "jugadores": [
            {"id_jugador": id_jugador, "id_comportamiento": 1}
            for id_jugador in [999, 1000, 1001, 1002, 1003, 1004]
        ],
        "duracion": 5,
        "formacion": "ofensiva",
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
        "jugadores": [
            {"id_jugador": id_jugador, "id_comportamiento": 1}
            for id_jugador in [1, 2, 3, 4, 5, 6]
        ],
        "duracion": 0,
        "formacion": "ofensiva",
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
        "jugadores": [
            {"id_jugador": id_jugador, "id_comportamiento": 1}
            for id_jugador in [1, 2, 3, 4, 5, 6]
        ],
        "duracion": 5,
        "formacion": "todos al arco",
    })

    assert response.status_code == 422

def test_crear_amistoso_comportamiento_inexistente(client, db_test):
    usuario = client.post("/usuario", json={
        "email": "pepito@gmail.com",
        "nombre": "Pepito",
        "avatar": 1,
        "contraseña": "asd123",
        "club": "Boca"
    })
    usuario_id = usuario.json()["id"]

    jugadores = crear_jugadores_test(db_test, usuario_id)

    response = client.post(f"/partido/{usuario_id}", json={
        "jugadores": [
            {"id_jugador": jugador.id_jugador, "id_comportamiento": 999}
            for jugador in jugadores
        ],
        "duracion": 5,
        "formacion": "ofensiva",
    })

    assert response.status_code == 404
    assert response.json() == {
        "error": "COMPORTAMIENTO_NO_ENCONTRADO",
        "mensaje": "El jugador no tiene un comportamiento válido"
    }

def test_listar_amistosos_disponibles(client, db_test):
    usuario = client.post("/usuario", json={
        "email": "tomas@gmail.com",
        "nombre": "tomas",
        "avatar": 1,
        "contraseña": "hola123",
        "club": "Talleres"
    })
    usuario_id = usuario.json()['id']

    jugadores = crear_jugadores_test(db_test, usuario_id)
    comportamiento = db_test.query(Comportamiento).filter_by(id_usuario=usuario_id).first()

    lista_partidos = client.get("/partidos")
    assert lista_partidos.status_code == 200
    assert len (lista_partidos.json()) == 0 # verifico que este vacia

    # creo un partido
    client.post(f"/partido/{usuario_id}", json={
        "jugadores": [{"id_jugador": j.id_jugador, "id_comportamiento": comportamiento.id} for j in jugadores],
        "duracion": 10,
        "formacion": "ofensiva",
    })

    lista_partidos = client.get("/partidos")
    assert lista_partidos.status_code == 200
    
    datos = lista_partidos.json()
    assert len(datos) == 1
    assert datos[0]["id"] is not None
    assert datos[0]["nombre"] == "Partido de tomas"


def test_listar_amistosos_disponibles_devuelve_error_interno(client):
    servicio = Mock()
    servicio.listar_amistosos_disponibles.side_effect = RuntimeError("fallo")
    client.app.dependency_overrides[obtener_servicio] = crear_override_servicio(servicio)

    response = client.get("/partidos")

    assert response.status_code == 500
    assert response.json() == {
        "error": "ERROR_INTERNO",
        "mensaje": "Ocurrió un error interno del servidor",
    }

def test_iniciar_partido(client, db_test, monkeypatch):
    partido, usuario_id = crear_partido_pendiente_test(client, db_test)

    estado = Mock()
    motor = Mock()
    ejecutor = Mock()

    ejecutar = Mock()
    ejecutor.ejecutar = ejecutar

    monkeypatch.setattr("app.capa_3_api.routers.partidos.crear_estado_partido", Mock(return_value=estado))

    monkeypatch.setattr("app.capa_3_api.routers.partidos.MotorPartido", Mock(return_value=motor))

    monkeypatch.setattr("app.capa_3_api.routers.partidos.EjecutorPartido", Mock(return_value=ejecutor))

    create_task = Mock()

    monkeypatch.setattr("app.capa_3_api.routers.partidos.asyncio.create_task", create_task)

    emitir_lobby = AsyncMock()

    monkeypatch.setattr(admin_conexiones, "emitir_lobby", emitir_lobby)

    respuesta = client.put(f"/partido/{partido.id_partido}/{usuario_id}")

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["mensaje"] == "Partido amistoso iniciado"
    assert datos["id_partido"] == partido.id_partido

    assert datos["cancha"]["ancho"] == 100
    assert datos["cancha"]["alto"] == 60

    assert datos["cancha"]["arco_izquierdo"] == {
        "poste_superior": {
            "x": 0,
            "y": 40
        },
        "poste_inferior": {
            "x": 0,
            "y": 20
        }
    }

    assert datos["cancha"]["arco_derecho"] == {
        "poste_superior": {
            "x": 100,
            "y": 40
        },
        "poste_inferior": {
            "x": 100,
            "y": 20
        }
    }


    assert partido.estado_partido == EstadoPartido.EN_CURSO

def test_realizar_cambio_jugador_correctamente(client, db_test, monkeypatch):
    partido, usuario_id = crear_partido_pendiente_test(client, db_test)
    jugadores = preparar_jugadores_equipo_test(db_test, usuario_id, partido.id_equipo_1)

    jugador_sale = jugadores[0]
    jugador_entra = jugadores[3]

    ejecutor = Mock()
    ejecutor.solicitar_cambio = AsyncMock()

    obtener = Mock(return_value=ejecutor)
    monkeypatch.setattr("app.capa_3_api.routers.partidos.administrador_partidas.obtener", obtener)

    response = client.put(f"/partido/{partido.id_partido}/{usuario_id}/cambio",
        json={
            "jugador_sale_id": jugador_sale.id_jugador,
            "jugador_entra_id": jugador_entra.id_jugador})

    assert response.status_code == 200
    assert response.json() == {"mensaje": "Solicitud de cambio recibida"}

def test_realizar_cambio_jugador_partido_no_en_ejecucion(client, db_test, monkeypatch):
    partido, usuario_id = crear_partido_pendiente_test(client, db_test)
    obtener = Mock(return_value=None)
    monkeypatch.setattr("app.capa_3_api.routers.partidos.administrador_partidas.obtener", obtener)

    response = client.put(
        f"/partido/{partido.id_partido}/{usuario_id}/cambio",
        json={
            "jugador_sale_id": 1,
            "jugador_entra_id": 2
        })

    assert response.status_code == 404
    assert response.json() == {
        "error": "PARTIDO_NO_ENCONTRADO",
        "mensaje": "El partido no existe o no se encuentra en ejecucion"}


def test_realizar_cambio_jugador_usuario_no_participa(client, db_test, monkeypatch):
    partido, usuario_id = crear_partido_pendiente_test(client, db_test)
    jugadores = preparar_jugadores_equipo_test(db_test, usuario_id, partido.id_equipo_1)

    jere = client.post("/usuario", json={
        "email": "juan1@gmail.com",
        "nombre": "juan",
        "avatar": 3,
        "contraseña": "juan123",
        "club": "river"})

    otro_usuario_id = jere.json()["id"]

    ejecutor = Mock()
    ejecutor.solicitar_cambio = AsyncMock()

    obtener = Mock(return_value=ejecutor)

    monkeypatch.setattr("app.capa_3_api.routers.partidos.administrador_partidas.obtener", obtener)

    response = client.put(
        f"/partido/{partido.id_partido}/{otro_usuario_id}/cambio",
        json={
            "jugador_sale_id": jugadores[0].id_jugador,
            "jugador_entra_id": jugadores[3].id_jugador})

    assert response.status_code == 404
    assert response.json() == {
        "error": "USUARIO_NO_ENCONTRADO",
        "mensaje": "El usuario no participa en este partido"}
    
def test_realizar_cambio_jugador_mismo_jugador(client, db_test, monkeypatch):
    partido, usuario_id = crear_partido_pendiente_test(client, db_test)
    jugadores = preparar_jugadores_equipo_test(db_test, usuario_id, partido.id_equipo_1)
    ejecutor = Mock()
    ejecutor.solicitar_cambio = AsyncMock()

    obtener = Mock(return_value=ejecutor)

    monkeypatch.setattr("app.capa_3_api.routers.partidos.administrador_partidas.obtener", obtener)

    jugador_id = jugadores[0].id_jugador

    response = client.put(
        f"/partido/{partido.id_partido}/{usuario_id}/cambio",
        json={
            "jugador_sale_id": jugador_id,
            "jugador_entra_id": jugador_id})

    assert response.status_code == 400
    assert response.json() == {
        "error": "NO_SE_PUEDE_CAMBIAR_JUGADOR",
        "mensaje": "No se puede realizar el cambio solicitado"}



def test_cambiar_comportamiento_correctamente(client, db_test, monkeypatch):
    partido, usuario_id = crear_partido_pendiente_test(client, db_test)
    jugadores = preparar_jugadores_equipo_test(db_test, usuario_id, partido.id_equipo_1)

    jugador = jugadores[0]

    comportamientos = (db_test.query(Comportamiento).filter(Comportamiento.id_usuario == usuario_id).all())

    comportamiento = comportamientos[1]

    ejecutor = Mock()
    obtener = Mock(return_value=ejecutor)

    monkeypatch.setattr("app.capa_3_api.routers.partidos.administrador_partidas.obtener", obtener)

    response = client.put(
        f"/partido/{partido.id_partido}/cambiar/comportamiento",
        json={
            "usuario_id": usuario_id,
            "jugador_id": jugador.id_jugador,
            "comp_id": comportamiento.id})

    assert response.status_code == 200

    assert response.json() == {
        "mensaje": "solicitud de cambio de comportamiento recibida",
        "Nuevo_comportamiento": comportamiento.nombre}
    
def test_cambiar_comportamiento_comportamiento_no_encontrado(client, db_test, monkeypatch):
    partido, usuario_id = crear_partido_pendiente_test(client, db_test)
    jugadores = preparar_jugadores_equipo_test(db_test, usuario_id, partido.id_equipo_1)

    otro_usuario = client.post("/usuario", json={
        "email": "jjj@gmail.com",
        "nombre": "jjj",
        "avatar": 3,
        "contraseña": "adgsdgf",
        "club": "Ninguno"})

    otro_usuario_id = otro_usuario.json()["id"]

    comportamiento_otro_usuario = (db_test.query(Comportamiento).filter(Comportamiento.id_usuario == otro_usuario_id).first())
    ejecutor = Mock()
    obtener = Mock(return_value=ejecutor)

    monkeypatch.setattr("app.capa_3_api.routers.partidos.administrador_partidas.obtener", obtener)

    response = client.put(
        f"/partido/{partido.id_partido}/cambiar/comportamiento",
        json={
            "usuario_id": usuario_id,
            "jugador_id": jugadores[0].id_jugador,
            "comp_id": comportamiento_otro_usuario.id})

    assert response.status_code == 400

    assert response.json() == {
        "error": "NO_SE_PUEDE_CAMBIAR_COMPORTAMIENTO",
        "mensaje": "No se puede realizar el cambio de comportamiento solicitado"}

def test_obtener_usuario_de_partido_devuelve_datos_y_emite_evento_websocket(client, db_test):
    partido, _ = crear_partido_pendiente_test(client, db_test)
    equipos_y_jugadores = {
        partido.id_usuario_1: (partido.id_equipo_1, preparar_jugadores_equipo_test(
            db_test, partido.id_usuario_1, partido.id_equipo_1)),
        partido.id_usuario_2: (partido.id_equipo_2, preparar_jugadores_equipo_test(
            db_test, partido.id_usuario_2, partido.id_equipo_2))
    }

    with client.websocket_connect(f"/ws/partido/{partido.id_partido}") as websocket:
        for usuario_id, (equipo_id, jugadores) in equipos_y_jugadores.items():
            response = client.get(f"/partido/{partido.id_partido}/{usuario_id}")

            assert response.status_code == 200
            datos = response.json()
            usuario = db_test.get(Usuario, usuario_id)
            assert datos["usuario"] == {
                "id": usuario_id,
                "nombre": usuario.nombre,
                "club": usuario.nombre_club,
                "avatar": usuario.id_avatar,
            }
            assert datos["id_equipo"] == equipo_id
            assert datos["formacion"] == (
                partido.formacion_1.value
                if usuario_id == partido.id_usuario_1
                else partido.formacion_2.value
            )
            asociaciones = db_test.get(Equipo, equipo_id).jugadores
            jugadores_por_id = {jugador["id"]: jugador for jugador in datos["jugadores"]}
            assert set(jugadores_por_id) == {jugador.id_jugador for jugador in jugadores}
            for asociacion in asociaciones:
                jugador = jugadores_por_id[asociacion.id_jugador]
                assert jugador == {
                    "id": asociacion.jugador.id_jugador,
                    "nombre": asociacion.jugador.nombre_jugador,
                    "estado": asociacion.estado.value,
                    "comportamiento": {
                        "id": asociacion.comportamiento.id,
                        "nombre": asociacion.comportamiento.nombre,
                    },
                }

            payload_websocket = {
                "avatar": usuario.id_avatar,
                "jugadores": [
                    {
                        "id": asociacion.jugador.id_jugador,
                        "nombre": asociacion.jugador.nombre_jugador,
                    }
                    for asociacion in asociaciones
                ]}
            assert websocket.receive_json() == {
                "action": "informacion_usuario_partido",
                "payload": payload_websocket}


def test_obtener_usuario_de_partido_mapea_partido_no_encontrado(client, db_test):
    partido_id_inexistente = 51
    assert db_test.get(Partido, partido_id_inexistente) is None

    response = client.get(f"/partido/{partido_id_inexistente}/10")

    assert response.status_code == 404
    assert response.json()["error"] == "PARTIDO_NO_ENCONTRADO"


def test_obtener_usuario_de_partido_mapea_usuario_no_encontrado(client, db_test):
    partido, _ = crear_partido_pendiente_test(client, db_test)
    usuario_que_no_participa = 999

    response = client.get(f"/partido/{partido.id_partido}/{usuario_que_no_participa}")

    assert response.status_code == 404
    assert response.json()["error"] == "USUARIO_NO_ENCONTRADO"


def test_obtener_usuario_de_partido_mapea_equipo_no_encontrado(client, db_test):
    partido, _ = crear_partido_pendiente_test(client, db_test)
    partido.id_equipo_2 = None
    db_test.commit()

    response = client.get(f"/partido/{partido.id_partido}/{partido.id_usuario_2}")

    assert response.status_code == 404
    assert response.json()["error"] == "EQUIPO_NO_ENCONTRADO"