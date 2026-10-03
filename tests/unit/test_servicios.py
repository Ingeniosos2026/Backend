from unittest.mock import Mock

import pytest

from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento
from app.capa_0_definicion_bd.models.partidos_modelos import Partido, TipoPartido, EstadoPartido, Formacion
from app.capa_2_logica.errores import *
from app.capa_2_logica.servicios import Servicios, password_hash
from app.capa_2_logica.resultados import *


def test_crear_usuario_datos_invalidos():

    repositorio = Mock()
    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(DatosInvalidos):
        servicio.crear_usuario(
            email="leandro@gmail.com.ar",
            nombre="Leandro",
            id_avatar=1,
            contraseña="123456",
            nombre_club="Talleres"
        )

    repositorio.obtener_por_email.assert_not_called()
    repositorio.crear.assert_not_called()


def test_crear_usuario_nombre_vacio():

    repositorio = Mock()
    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(DatosInvalidos):
        servicio.crear_usuario(
            email="leandro@gmail.com",
            nombre="",
            id_avatar=1,
            contraseña="123456",
            nombre_club="Talleres"
        )

    repositorio.obtener_por_email.assert_not_called()
    repositorio.crear.assert_not_called()

def test_crear_usuario_contraseña_vacia():

    repositorio = Mock()
    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(DatosInvalidos):
        servicio.crear_usuario(
            email="leandro@gmail.com",
            nombre="Leandro",
            id_avatar=1,
            contraseña="",
            nombre_club="Talleres"
        )

    repositorio.obtener_por_email.assert_not_called()
    repositorio.crear.assert_not_called()

def test_crear_usuario_club_vacio():

    repositorio = Mock()
    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(DatosInvalidos):
        servicio.crear_usuario(
            email="leandro@gmail.com",
            nombre="Leandro",
            id_avatar=1,
            contraseña="123456",
            nombre_club=""
        )

    repositorio.obtener_por_email.assert_not_called()
    repositorio.crear.assert_not_called()

def test_crear_usuario_email_registrado():

    repositorio = Mock()

    usuario_existente = Usuario(
        email="leandro@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="123456",
        nombre_club="Talleres"
    )

    repositorio.obtener_por_email.return_value = usuario_existente

    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(EmailRegistrado):
        servicio.crear_usuario(
            email="leandro@gmail.com",
            nombre="Leandro",
            id_avatar=1,
            contraseña="123456",
            nombre_club="Talleres"
        )

    repositorio.obtener_por_email.assert_called_once_with("leandro@gmail.com")
    repositorio.crear.assert_not_called()


def test_crear_usuario_correctamente():

    repositorio = Mock()
    repositorio.obtener_por_email.return_value = None

    usuario_nuevo = Usuario(
        id_usuario=1,
        email="leandro@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="hash",
        nombre_club="Talleres"
    )

    repositorio.crear.return_value = usuario_nuevo
    servicio = Servicios(usuarios=repositorio)

    resultado = servicio.crear_usuario(
        email="leandro@gmail.com",
        nombre="Leandro",
        id_avatar=1,
        contraseña="123456",
        nombre_club="Talleres"
    )

    usuario = resultado.usuario

    assert usuario.id_usuario == 1
    assert usuario.email == "leandro@gmail.com"
    assert usuario.nombre == "Leandro"
    assert usuario.id_avatar == 1
    assert usuario.nombre_club == "Talleres"
    usuario_creado = repositorio.crear.call_args.args[0]
    assert [comportamiento.nombre for comportamiento in usuario_creado.comportamientos] == [
        "Defender",
        "Atacar",
        "Pasar compañero",
    ]

    assert usuario.contraseña != "123456"
    assert usuario.contraseña is not None

    repositorio.obtener_por_email.assert_called_once_with("leandro@gmail.com")
    repositorio.crear.assert_called_once()

def test_login_usuario_correctamente():
    contraseña = "asd123"

    repositorio = Mock()
    usuario = Usuario(
        id_usuario=1,
        email="pepito@gmail.com",
        nombre="Pepitocabj",
        id_avatar=1,
        contraseña=password_hash.hash(contraseña),
        nombre_club="boca"
    )

    repositorio.obtener_por_email.return_value = usuario

    servicio = Servicios(usuarios=repositorio)

    resultado = servicio.login_usuario(
        email="pepito@gmail.com",
        contraseña=contraseña
    )

    assert resultado == usuario

    repositorio.obtener_por_email.assert_called_once_with("pepito@gmail.com")

def test_login_contraseña_incorrecta():

    repositorio = Mock()
    usuario = Usuario(
        id_usuario=1,
        email="pepito@gmail.com",
        nombre="Pepitocabj",
        id_avatar=1,
        contraseña=password_hash.hash("asd123"),
        nombre_club="boca"
    )

    repositorio.obtener_por_email.return_value = usuario

    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(CredencialesInvalidas):
        servicio.login_usuario(
            email="pepito@gmail.com",
            contraseña= "contraseña_incorrecta"
        )

def test_login_usuario_inexistente():
    repositorio = Mock()
    repositorio.obtener_por_email.return_value = None

    servicio = Servicios(usuarios=repositorio)

    with pytest.raises(CredencialesInvalidas):
        servicio.login_usuario(
            email="inexistente@gmail.com",
            contraseña="asd123"
        )

    repositorio.obtener_por_email.assert_called_once_with(
        "inexistente@gmail.com"
    )

def test_crear_amistoso_correctamente():
    repo_equipos = Mock()
    repo_partidos = Mock()
    repo_usuarios = Mock()

    equipo = Equipo(
        id_equipo=1,
        id_usuario=1
    )
    jugadores = [
        Jugador(
            id_jugador=id_jugador,
            id_usuario=1,
            id_comportamiento=7,
            nombre_jugador=f"Jugador {id_jugador}",
            poder=60,
            agilidad=60,
            control=60,
            velocidad=60,
            fuerza=60,
        )
        for id_jugador in range(1, 7)
    ]
    jugadores_por_id = {jugador.id_jugador: jugador for jugador in jugadores}

    repo_usuarios.obtener_por_id.return_value = Usuario(id_usuario=1)
    repo_equipos.crear.return_value = equipo
    repo_equipos.obtener_por_id.return_value = equipo
    repo_equipos.agregar_jugador.side_effect = agregar_jugador
    repo_jugadores = Mock()
    repo_jugadores.obtener_por_id.side_effect = jugadores_por_id.get
    repo_comportamientos = Mock()
    repo_comportamientos.obtener_comportamiento_por_id_y_usuario.return_value = Comportamiento(
        id=7,
        id_usuario=1,
        nombre="Defender",
        codigo="def comportamiento(primitivas): pass",
    )

    partido_nuevo = Partido(
        id_partido=1,
        id_usuario_1=1,
        id_usuario_2=None,
        id_equipo_1=1,
        id_equipo_2=None,
        duracion=5,
        formacion=Formacion.FORMACION_1,
        tipo=TipoPartido.AMISTOSO,
        estado=EstadoPartido.DISPONIBLE
    )

    repo_partidos.crear.return_value = partido_nuevo

    servicio = Servicios(usuarios=repo_usuarios, equipos=repo_equipos, jugadores=repo_jugadores, partidos=repo_partidos, comportamientos=repo_comportamientos)
    resultado = servicio.crear_amistoso(
        usuario_id=1,
        jugadores_comportamientos=[
            (id_jugador, 7) for id_jugador in jugadores_por_id
        ],
        duracion=5,
        formacion=Formacion.FORMACION_1,
    )

    assert resultado.partido == partido_nuevo
    assert partido_nuevo.id_usuario_1 == 1
    assert partido_nuevo.id_equipo_1 == 1
    assert partido_nuevo.duracion == 5
    assert partido_nuevo.formacion == Formacion.FORMACION_1
    assert partido_nuevo.id_usuario_2 is None
    assert partido_nuevo.id_equipo_2 is None
    assert partido_nuevo.tipo == TipoPartido.AMISTOSO
    assert partido_nuevo.estado == EstadoPartido.DISPONIBLE
    assert equipo.jugadores_amistosos == jugadores

    repo_usuarios.obtener_por_id.assert_called_once_with(1)
    repo_equipos.crear.assert_called_once()
    assert repo_equipos.agregar_jugador.call_count == 6
    repo_partidos.crear.assert_called_once()

def test_crear_amistoso_jugador_no_encontrado():
    repo_equipos = Mock()
    repo_partidos = Mock()
    repo_usuarios = Mock()
    repo_jugadores = Mock()
    repo_usuarios.obtener_por_id.return_value = Usuario(id_usuario=1)
    repo_jugadores.obtener_por_id.return_value = None

    servicio = Servicios(usuarios=repo_usuarios, equipos=repo_equipos, jugadores=repo_jugadores, partidos=repo_partidos)

    with pytest.raises(JugadorNoEncontrado):
        servicio.crear_amistoso(
            usuario_id=1,
            jugadores_comportamientos=[(id_jugador, 7) for id_jugador in range(1, 7)],
            duracion=5,
            formacion=Formacion.FORMACION_1,
        )

    repo_equipos.crear.assert_not_called()
    repo_partidos.crear.assert_not_called()

def test_crear_amistoso_comportamiento_no_encontrado():
    repo_equipos = Mock()
    repo_partidos = Mock()
    repo_usuarios = Mock()
    repo_jugadores = Mock()
    repo_comportamientos = Mock()
    repo_usuarios.obtener_por_id.return_value = Usuario(id_usuario=1)
    repo_comportamientos.obtener_comportamiento_por_id_y_usuario.return_value = None
    repo_jugadores.obtener_por_id.return_value = Jugador(
        id_jugador=1,
        id_usuario=1,
        nombre_jugador="Jugador 1",
        poder=60,
        agilidad=60,
        control=60,
        velocidad=60,
        fuerza=60,
    )
    servicio = Servicios(
        usuarios=repo_usuarios,
        equipos=repo_equipos,
        jugadores=repo_jugadores,
        partidos=repo_partidos,
        comportamientos=repo_comportamientos,
    )

    with pytest.raises(ComportamientoNoEncontrado):
        servicio.crear_amistoso(
            usuario_id=1,
            jugadores_comportamientos=[(id_jugador, 999) for id_jugador in range(1, 7)],
            duracion=5,
            formacion=Formacion.FORMACION_1,
        )

    repo_equipos.crear.assert_not_called()
    repo_partidos.crear.assert_not_called()

def test_crear_amistoso_duracion_invalida():
    repo_equipos = Mock()
    repo_partidos = Mock()
    repo_usuarios = Mock()
    repo_jugadores = Mock()

    servicio = Servicios( usuarios=repo_usuarios, equipos=repo_equipos, jugadores=repo_jugadores, partidos=repo_partidos)

    with pytest.raises(DatosInvalidos):
        servicio.crear_amistoso(
            usuario_id=1,
            jugadores_comportamientos=[],
            duracion=0,
            formacion=Formacion.FORMACION_1,
        )

    repo_equipos.crear.assert_not_called()
    repo_jugadores.obtener_por_id.assert_not_called()
    repo_partidos.crear.assert_not_called()

def test_crear_amistoso_formacion_invalida():
    repo_equipos = Mock()
    repo_partidos = Mock()
    repo_usuarios = Mock()
    repo_jugadores = Mock()
    servicio = Servicios(
        usuarios=repo_usuarios,
        equipos=repo_equipos,
        jugadores=repo_jugadores,
        partidos=repo_partidos,
    )

    with pytest.raises(DatosInvalidos):
        servicio.crear_amistoso(
            usuario_id=1,
            jugadores_comportamientos=[(id_jugador, 7) for id_jugador in range(1, 7)],
            duracion=5,
            formacion=5,
        )

    repo_jugadores.obtener_por_id.assert_not_called()
    repo_equipos.crear.assert_not_called()
    repo_partidos.crear.assert_not_called()

def agregar_jugador(equipo, jugador):
    equipo.jugadores_amistosos.append(jugador)
    jugador.id_equipo = equipo.id_equipo
    return equipo

def test_agregar_jugador_a_equipo_correctamente():
    repo_equipos = Mock()
    repo_jugadores = Mock()
    repo_usuarios = Mock()

    equipo = Equipo(
        id_equipo=1,
        id_usuario=1
    )

    jugador = Jugador(
        id_jugador=1,
        id_usuario=1,
        nombre_jugador="Messi",
        poder=60,
        agilidad=60,
        control=60,
        velocidad=60,
        fuerza=60
    )

    repo_equipos.obtener_por_id.return_value = equipo
    repo_jugadores.obtener_por_id.return_value = jugador
    repo_equipos.agregar_jugador.side_effect = agregar_jugador
    repo_usuarios.obtener_por_email.return_value = Usuario(id_usuario=1)
    comportamiento = Comportamiento(
        id=1,
        id_usuario=1,
        nombre="Defender",
        codigo="def comportamiento(primitivas): pass",
    )
    repo_comportamientos = Mock()
    repo_comportamientos.obtener_comportamiento_por_id_y_usuario.return_value = comportamiento
    servicio = Servicios(usuarios=repo_usuarios, equipos=repo_equipos, jugadores=repo_jugadores, comportamientos=repo_comportamientos)
    resultado = servicio.agregar_jugador_a_equipo(
        usuario_id=1,
        id_equipo=1,
        id_jugador=1,
        id_comportamiento=1,
    )

    assert resultado.equipo == equipo
    assert jugador.comportamiento is comportamiento
    assert jugador in equipo.jugadores_amistosos
    assert jugador.id_equipo == equipo.id_equipo

    repo_equipos.obtener_por_id.assert_called_once_with(1)
    repo_jugadores.obtener_por_id.assert_called_once_with(1)
    repo_equipos.agregar_jugador.assert_called_once_with(equipo, jugador)

def test_agregar_jugador_a_equipo_equipo_no_encontrado():
    repo_equipos = Mock()
    repo_jugadores = Mock()
    repo_usuarios = Mock()

    repo_equipos.obtener_por_id.return_value = None

    servicio = Servicios(usuarios=repo_usuarios, equipos=repo_equipos, jugadores=repo_jugadores)

    with pytest.raises(EquipoNoEncontrado):
        servicio.agregar_jugador_a_equipo(usuario_id=1, id_equipo=58, id_jugador=1, id_comportamiento=1)

    repo_equipos.obtener_por_id.assert_called_once_with(58)
    repo_jugadores.obtener_por_id.assert_not_called()
    repo_equipos.agregar_jugador.assert_not_called()

def test_agregar_jugador_a_equipo_usuario_no_encontrado():
    repo_equipos = Mock()
    repo_jugadores = Mock()
    repo_usuarios = Mock()

    equipo = Equipo(
        id_equipo=1,
        id_usuario=2
    )

    repo_equipos.obtener_por_id.return_value = equipo

    servicio = Servicios(usuarios=repo_usuarios, equipos=repo_equipos, jugadores=repo_jugadores)

    with pytest.raises(UsuarioNoEncontrado):
        servicio.agregar_jugador_a_equipo(usuario_id=1, id_equipo=1, id_jugador=1, id_comportamiento=1)

    repo_equipos.obtener_por_id.assert_called_once_with(1)
    repo_jugadores.obtener_por_id.assert_not_called()
    repo_equipos.agregar_jugador.assert_not_called()

def test_agregar_jugador_a_equipo_jugador_no_encontrado():
    repo_equipos = Mock()
    repo_jugadores = Mock()
    repo_usuarios = Mock()

    equipo = Equipo(
        id_equipo=1,
        id_usuario=1
    )

    repo_equipos.obtener_por_id.return_value = equipo
    repo_jugadores.obtener_por_id.return_value = None

    servicio = Servicios(usuarios=repo_usuarios, equipos=repo_equipos, jugadores=repo_jugadores)

    with pytest.raises(JugadorNoEncontrado):
        servicio.agregar_jugador_a_equipo(usuario_id=1, id_equipo=1, id_jugador=58, id_comportamiento=1)

    repo_equipos.obtener_por_id.assert_called_once_with(1)
    repo_jugadores.obtener_por_id.assert_called_once_with(58)
    repo_equipos.agregar_jugador.assert_not_called()

def test_agregar_jugador_a_equipo_con_comportamiento():
    repo_equipos = Mock()
    repo_jugadores = Mock()
    repo_usuarios = Mock()
    repo_comportamientos = Mock()

    equipo = Equipo(id_equipo=1, id_usuario=1)
    jugador = Jugador(
        id_jugador=1,
        id_usuario=1,
        nombre_jugador="Messi",
        poder=60,
        agilidad=60,
        control=60,
        velocidad=60,
        fuerza=60,
    )
    comportamiento = Comportamiento(
        id=7,
        id_usuario=1,
        nombre="Defender",
        codigo="def comportamiento(jugador): pass",
    )

    repo_equipos.obtener_por_id.return_value = equipo
    repo_jugadores.obtener_por_id.return_value = jugador
    repo_comportamientos.obtener_comportamiento_por_id_y_usuario.return_value = comportamiento
    repo_equipos.agregar_jugador.side_effect = agregar_jugador

    servicio = Servicios(
        usuarios=repo_usuarios,
        jugadores=repo_jugadores,
        comportamientos=repo_comportamientos,
        equipos=repo_equipos,
    )

    resultado = servicio.agregar_jugador_a_equipo(
        usuario_id=1,
        id_equipo=1,
        id_jugador=1,
        id_comportamiento=7,
    )

    assert resultado.equipo == equipo
    assert jugador.comportamiento is comportamiento
    assert jugador in equipo.jugadores_amistosos
    repo_comportamientos.obtener_comportamiento_por_id_y_usuario.assert_called_once_with(7, 1)
    repo_equipos.agregar_jugador.assert_called_once_with(equipo, jugador)

def test_agregar_jugador_a_equipo_comportamiento_no_encontrado():
    repo_equipos = Mock()
    repo_jugadores = Mock()
    repo_usuarios = Mock()
    repo_comportamientos = Mock()

    repo_equipos.obtener_por_id.return_value = Equipo(id_equipo=1, id_usuario=1)
    repo_jugadores.obtener_por_id.return_value = Jugador(id_jugador=1, id_usuario=1)
    repo_comportamientos.obtener_comportamiento_por_id_y_usuario.return_value = None

    servicio = Servicios(
        usuarios=repo_usuarios,
        jugadores=repo_jugadores,
        comportamientos=repo_comportamientos,
        equipos=repo_equipos,
    )

    with pytest.raises(ComportamientoNoEncontrado):
        servicio.agregar_jugador_a_equipo(
            usuario_id=1,
            id_equipo=1,
            id_jugador=1,
            id_comportamiento=7,
        )

    repo_equipos.agregar_jugador.assert_not_called()