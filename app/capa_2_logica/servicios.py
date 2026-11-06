import re
from typing import Protocol
from pwdlib import PasswordHash
import random
from itertools import combinations

from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador as JugadorModelo
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento as ComportamientoModelo
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo as EquipoModelo
from app.capa_0_definicion_bd.models.equipos_jugadores_modelos import EstadoJugador, EquipoJugador
from app.capa_0_definicion_bd.models.partidos_modelos import Partido as PartidoModelo, TipoPartido, EstadoPartido, Formacion
from app.capa_0_definicion_bd.models.liga_modelos import Liga as LigaModelo
from app.partido.validador import CodigoComportamientoInvalido, validar_codigo_comportamiento
from app.capa_0_definicion_bd.models.liga_modelos import EstadoLiga, Liga as LigaModelo
from app.capa_0_definicion_bd.models.liga_participantes_modelos import LigaParticipante
from app.capa_0_definicion_bd.models.fixture_liga_modelos import FixtureLiga
from app.capa_0_definicion_bd.models.tabla_liga_modelos import TablaLiga
from app.partido.comportamientos import COMPORTAMIENTOS_PREDETERMINADOS
from sqlalchemy.exc import IntegrityError
from .errores import *
from .resultados import *

password_hash = PasswordHash.recommended()

class _RepoUsuariosProtocol(Protocol):
    def crear (self, usuario: UsuarioModelo) -> UsuarioModelo: ...
    def obtener_por_email(self, email: str) -> UsuarioModelo | None: ...
    def obtener_por_id(self, id_usuario: int) -> UsuarioModelo | None: ...

class _RepoJugadoresProtocol(Protocol):
    def crear(self, jugador: JugadorModelo) -> JugadorModelo: ...
    def obtener_por_id(self, id_jugador: int) -> JugadorModelo | None: ...
    def contar_jugadores_usuario(self, id_usuario: int) -> int: ...
    def obtener_jugadores_disponibles(self, id_usuario: int) -> list[JugadorModelo]: ...

class _RepoComportamientosProtocol(Protocol):
    def obtener_comportamiento_por_id_y_usuario(self, comp_id: int, usuario_id: int) -> ComportamientoModelo | None: ...
    def obtener_comportamientos_usuario(self, usuario_id: int) -> List[ComportamientoModelo]: ...
    def crear(self, comportamiento: ComportamientoModelo) -> ComportamientoModelo: ...
    def actualizar(self, comportamiento: ComportamientoModelo) -> ComportamientoModelo: ...
    def eliminar(self, comportamiento: ComportamientoModelo) -> None: ...

class _RepoPartidosProtocol(Protocol):
    def crear(self, partido: PartidoModelo) -> PartidoModelo: ...
    def obtener_amistosos_disponibles(self) -> list[PartidoModelo]: ...
    def obtener_por_id(self, id_partido: int) -> PartidoModelo | None: ...
    def actualizar(self, partido: PartidoModelo) -> PartidoModelo: ...

class _RepoEquiposProtocol(Protocol):
    def crear(self, equipo: EquipoModelo) -> EquipoModelo: ...
    def obtener_por_id(self, id_equipo: int) -> EquipoModelo | None: ...
    def agregar_jugador(self, equipo: EquipoModelo, jugador: JugadorModelo, estado: EstadoJugador, comportamiento: ComportamientoModelo | None = None) -> EquipoModelo: ...
    def obtener_jugador_equipo(self, id_equipo: int, id_jugador: int) -> EquipoJugador | None: ...

class _RepoLigasProtocol(Protocol):
    def crear(self, liga: LigaModelo) -> LigaModelo: ...
    def obtener_por_id(self, id_liga: int) -> LigaModelo | None: ...
    def agregar_participante(self, liga: LigaModelo, usuario: UsuarioModelo, id_equipo: int, formacion: Formacion) -> LigaParticipante: ...
    def eliminar_participante(self, liga: LigaModelo, usuario: UsuarioModelo) -> LigaModelo: ...
    def obtener_ligas_disponibles(self) -> list[LigaModelo]: ...
    def obtener_participantes_liga(self, id_liga: int) -> list[LigaParticipante]: ...
    def guardar_inicio_liga(self, liga: LigaModelo, tabla: list[TablaLiga], fixture: list[FixtureLiga],) -> None: ...
    def obtener_fixture_por_turno(self, id_liga: int, turno: int) -> FixtureLiga: ...
    def asignar_partido_fixture(self, fixture: FixtureLiga, partido_id: int) -> FixtureLiga: ...
    def obtener_siguiente_fixture(self, id_liga: int) -> FixtureLiga | None: ...
    def obtener_participante_por_equipo(self, id_liga: int, id_equipo: int) -> LigaParticipante | None: ...
    def obtener_registro_tabla(self, id_liga: int, id_equipo: int) -> TablaLiga | None: ...
    def finalizar_liga(self, liga: LigaModelo) -> LigaModelo: ...
    def actualizar(self) -> None: ...
    def obtener_fixture_completo(self, id_liga: int) -> list[FixtureLiga]: ...
    def obtener_tabla_completa(self, id_liga: int) -> list[TablaLiga]: ...


class Servicios:
    """" Servicios que implementan la logica del juego """

    def __init__(self, usuarios: _RepoUsuariosProtocol, jugadores: _RepoJugadoresProtocol = None, comportamientos: _RepoComportamientosProtocol = None, partidos: _RepoPartidosProtocol = None, equipos: _RepoEquiposProtocol = None, ligas: _RepoLigasProtocol = None):
        self.usuarios = usuarios
        self.jugadores = jugadores
        self.comportamientos = comportamientos
        self.partidos = partidos
        self.equipos = equipos
        self.ligas = ligas
    
    def email_valido(self, email: str) -> bool:
        patron = r"^[a-zA-Z0-9._%+-]+@(gmail|hotmail|outlook)\.com$"
        return re.match(patron, email) is not None
    
    def crear_usuario(self, email: str, nombre: str, id_avatar: int, contraseña: str, nombre_club: str) -> CrearUsuarioResultado:
        
        if not nombre.strip():
            raise DatosInvalidos

        if not contraseña.strip():
            raise DatosInvalidos

        if not nombre_club.strip():
            raise DatosInvalidos

        if not self.email_valido(email):
            raise DatosInvalidos
        
        if self.usuarios.obtener_por_email(email) is not None:
            raise EmailRegistrado
        

        hash_contraseña = password_hash.hash(contraseña)

        nuevo_usuario = UsuarioModelo(
            email=email,
            nombre=nombre,
            id_avatar=id_avatar,
            contraseña=hash_contraseña,
            nombre_club=nombre_club
        )
        nuevo_usuario.comportamientos = [
            ComportamientoModelo(nombre=nombre_comportamiento, codigo=codigo)
            for nombre_comportamiento, codigo in COMPORTAMIENTOS_PREDETERMINADOS
        ]

        usuario = self.usuarios.crear(nuevo_usuario)

        return CrearUsuarioResultado(usuario=usuario)

    def login_usuario(self, email: str, contraseña: str) -> UsuarioModelo:
        usuario = self.usuarios.obtener_por_email(email)
        if usuario is None:
            raise CredencialesInvalidas
        
        if not password_hash.verify(contraseña, usuario.contraseña):
            raise CredencialesInvalidas
        
        return usuario
    
    def crear_jugador(self, usuario_id: int, nombre: str, power: int, agility: int, control: int, speed: int, strength: int) -> CrearJugadorResultado:
        stats = [power, agility, control, speed, strength]
        
        if any(s < 20 or s > 100 for s in stats):
            raise DatosInvalidos()
        
        if sum(stats) != 300:
            raise DatosInvalidos()

        nuevo_jugador = JugadorModelo(
            id_usuario=usuario_id,
            nombre_jugador=nombre,
            poder=power,
            agilidad=agility,
            control=control,
            velocidad=speed,
            fuerza=strength
        )
        
        try:
            jugador = self.jugadores.crear(nuevo_jugador)
            return CrearJugadorResultado(jugador=jugador)
        except IntegrityError:
            raise DatosInvalidos() # so el usuario_id no existe en la bd, se dispara el error

    def obtener_comportamiento(self, usuario_id: int, comp_id: int) -> ObtenerComportamientoResultado:
        comportamiento = self.comportamientos.obtener_comportamiento_por_id_y_usuario(comp_id, usuario_id)
        
        if comportamiento is None:
            raise ComportamientoNoEncontrado()
            
        return ObtenerComportamientoResultado(comportamiento=comportamiento)

    
    def listar_comportamientos(self, usuario_id: int) -> ListarComportamientosResultado:
        comportamientos = self.comportamientos.obtener_comportamientos_usuario(usuario_id)
        
        if not comportamientos:
            raise ComportamientosNoEncontrados()
            
        return ListarComportamientosResultado(comportamientos=comportamientos)


    def crear_amistoso(self, usuario_id: int, duracion: int, jugadores_comportamientos: list[tuple[int, int]], formacion: Formacion) -> CrearPartidoResultado:
        if duracion <= 0:
            raise DatosInvalidos()

        try:
            formacion = Formacion(formacion)
        except (TypeError, ValueError) as error:
            raise DatosInvalidos() from error

        if len(jugadores_comportamientos) != 6:
            raise DatosInvalidos()

        ids_jugadores = [id_jugador for id_jugador, _ in jugadores_comportamientos]
        if len(set(ids_jugadores)) != 6:
            raise DatosInvalidos()

        jugadores = []
        for id_jugador, id_comportamiento in jugadores_comportamientos:
            jugador = self.jugadores.obtener_por_id(id_jugador)
            if jugador is None or jugador.id_usuario != usuario_id:
                raise JugadorNoEncontrado()
            comportamiento = self.comportamientos.obtener_comportamiento_por_id_y_usuario(
                id_comportamiento,
                usuario_id,
            )
            if comportamiento is None:
                raise ComportamientoNoEncontrado()
            jugadores.append((jugador, id_comportamiento))

        resultado_equipo = self.crear_equipo(usuario_id=usuario_id)
        equipo = resultado_equipo.equipo

        for indice, (jugador, id_comportamiento) in enumerate(jugadores):
            estado = (EstadoJugador.TITULAR if indice < 3 else EstadoJugador.SUPLENTE)
            resultado_equipo = self.agregar_jugador_a_equipo(
                usuario_id=usuario_id,
                id_equipo=equipo.id_equipo,
                id_jugador=jugador.id_jugador,
                id_comportamiento=id_comportamiento,
                estado=estado
            )
            equipo = resultado_equipo.equipo

        nuevo_partido = PartidoModelo(
            id_usuario_1=usuario_id,
            id_usuario_2=None,
            id_equipo_1=equipo.id_equipo,
            id_equipo_2=None,
            duracion_partido=duracion,
            formacion_1=formacion,
            formacion_2=None,
            tipo_partido=TipoPartido.AMISTOSO,
            estado_partido=EstadoPartido.DISPONIBLE
        )

        partido = self.partidos.crear(nuevo_partido)
        return CrearPartidoResultado(partido=partido)

    def crear_equipo(self, usuario_id: int) -> CrearEquipoResultado:
        nuevo_equipo = EquipoModelo(
            id_usuario=usuario_id
        )

        usuario = self.usuarios.obtener_por_id(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado()
        equipo = self.equipos.crear(nuevo_equipo)
        return CrearEquipoResultado(equipo=equipo)

    def agregar_jugador_a_equipo(self, usuario_id: int, id_equipo: int, id_jugador: int, id_comportamiento: int, estado: EstadoJugador) -> CrearEquipoResultado:
        equipo = self.equipos.obtener_por_id(id_equipo)
        if equipo is None:
            raise EquipoNoEncontrado()
        if equipo.id_usuario != usuario_id:
            raise UsuarioNoEncontrado()

        jugador = self.jugadores.obtener_por_id(id_jugador)
        if jugador is None or jugador.id_usuario != usuario_id:
            raise JugadorNoEncontrado()

        comportamiento = self.comportamientos.obtener_comportamiento_por_id_y_usuario(
            id_comportamiento,
            usuario_id,
        )
        if comportamiento is None:
            raise ComportamientoNoEncontrado()
        equipo_actualizado = self.equipos.agregar_jugador(equipo, jugador, estado, comportamiento)
        return CrearEquipoResultado(equipo=equipo_actualizado)

    def listar_amistosos_disponibles(self) -> ListarAmistososResultado:
        amistosos = self.partidos.obtener_partidos_amistosos_disponibles()
        return ListarAmistososResultado(amistosos=amistosos)

    def unirse_amistoso(self, partido_id: int, usuario_id: int, jugadores_comportamientos: list[tuple[int, int]], formacion: Formacion) -> UnirseAmistosoResultado:
        try:
            formacion = Formacion(formacion)
        except (TypeError, ValueError) as error:
            raise DatosInvalidos() from error

        partido = self.partidos.obtener_por_id(partido_id)

        if partido is None:
            raise PartidoNoEncontrado()

        if partido.tipo_partido != TipoPartido.AMISTOSO:
            raise DatosInvalidos()

        if partido.estado_partido != EstadoPartido.DISPONIBLE:
            raise PartidoNoDisponible()

        if partido.id_usuario_2 is not None:
            raise PartidoNoDisponible()

        usuario = self.usuarios.obtener_por_id(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado()

        cantidad_jugadores = self.jugadores.contar_jugadores_usuario(usuario_id)

        if cantidad_jugadores < 6:
            raise JugadoresInsuficientes()

        if len(jugadores_comportamientos) != 6:
            raise DatosInvalidos()

        id_jugadores = [id_jugador for id_jugador, _ in jugadores_comportamientos]

        if len(set(id_jugadores)) != 6:
            raise DatosInvalidos()

        jugadores = []

        for id_jugador, id_comportamiento in jugadores_comportamientos:
            jugador = self.jugadores.obtener_por_id(id_jugador)

            if jugador is None or jugador.id_usuario != usuario_id:
                raise JugadorNoEncontrado()

            comportamiento = (self.comportamientos.obtener_comportamiento_por_id_y_usuario(id_comportamiento, usuario_id))

            if comportamiento is None:
                raise ComportamientoNoEncontrado()
            jugadores.append((jugador, comportamiento))

        equipo = self.equipos.crear(EquipoModelo(id_usuario=usuario_id))

        for indice, (jugador, comportamiento) in enumerate(jugadores):
            estado = (EstadoJugador.TITULAR if indice < 3 else EstadoJugador.SUPLENTE)
            equipo = self.equipos.agregar_jugador(equipo, jugador, estado, comportamiento)

        partido.id_usuario_2 = usuario_id
        partido.id_equipo_2 = equipo.id_equipo
        partido.formacion_2 = formacion
        partido.estado_partido = EstadoPartido.PENDIENTE

        partido = self.partidos.actualizar(partido)

        return UnirseAmistosoResultado(partido=partido, usuario_unido=usuario)
    
    def listar_jugadores_disponibles(self, usuario_id: int) -> ListarJugadoresResultado:
        jugadores = self.jugadores.obtener_jugadores_disponibles(usuario_id)
        return ListarJugadoresResultado(jugadores=jugadores)

    def iniciar_partido(self, partido_id: int, usuario_id: int) -> PartidoResultado:

        partido = self.partidos.obtener_por_id(partido_id)

        if partido is None:
            raise AmistosoNoEncontrado()

        if partido.id_usuario_1 != usuario_id:
            raise IniciarNoPermitido()

        if partido.estado_partido != EstadoPartido.PENDIENTE:
            raise AmistosoNoPuedeIniciar()

        partido.estado_partido = EstadoPartido.EN_CURSO

        self.partidos.actualizar(partido)

        return PartidoResultado(partido=partido)

    def crear_liga(self, usuario_id: int, nombre: str, contraseña: str | None, min_jugadores: int, max_jugadores: int, duracion_partido: int, jugadores_comportamientos: list[tuple[int, int]], formacion: Formacion) -> CrearLigaResultado:

        if not nombre.strip():
            raise DatosLigaInvalidos()

        if min_jugadores < 3 or max_jugadores < 3:
            raise DatosLigaInvalidos()

        if min_jugadores > max_jugadores:
            raise DatosLigaInvalidos()

        if duracion_partido <= 0:
            raise DatosLigaInvalidos()

        usuario = self.usuarios.obtener_por_id(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado()
        
        cantidad_jugadores = self.jugadores.contar_jugadores_usuario(usuario_id)
        if cantidad_jugadores < 6:
            raise JugadoresInsuficientes()
        
        if len(jugadores_comportamientos) != 6:
            raise DatosInvalidos()
        
        jugadores = []
        for id_jugador, id_comportamiento in jugadores_comportamientos:
            jugador = self.jugadores.obtener_por_id(id_jugador)

            if jugador is None or jugador.id_usuario != usuario_id:
                raise JugadorNoEncontrado()
            
            comportamiento = self.comportamientos.obtener_comportamiento_por_id_y_usuario(id_comportamiento, usuario_id)
            if comportamiento is None:
                raise ComportamientoNoEncontrado()
            
            jugadores.append((jugador, id_comportamiento))

        resultado_equipo = self.crear_equipo(usuario_id=usuario_id)
        equipo = resultado_equipo.equipo
        for indice, (jugador, id_comportamiento) in enumerate(jugadores):
            estado = (EstadoJugador.TITULAR if indice < 3 else EstadoJugador.SUPLENTE)
            self.agregar_jugador_a_equipo(
                usuario_id=usuario_id, id_equipo=equipo.id_equipo, id_jugador=jugador.id_jugador,
                id_comportamiento=id_comportamiento, estado=estado
            ) # el for es para agregar los jugadores al equipo del usuario que crea la liga

        nueva_liga = LigaModelo(
            id_usuario=usuario_id,
            nombre=nombre.strip(),
            contraseña=contraseña,
            min_jugadores=min_jugadores,
            max_jugadores=max_jugadores,
            duracion_partido=duracion_partido,
        )

        liga = self.ligas.crear(nueva_liga)

        #ahora directamente agrego al owner de la liga como participante, con su equipo y formacion
        participacion = self.ligas.agregar_participante(liga, usuario, equipo.id_equipo, formacion)

        return CrearLigaResultado(liga=liga, participacion=participacion)

    def crear_comportamiento(self, usuario_id: int, nombre: str, codigo: str) -> CrearComportamientoResultado:
        if not nombre.strip():
            raise DatosInvalidos()

        if len(nombre) > 50:
            raise DatosInvalidos()

        usuario = self.usuarios.obtener_por_id(usuario_id)

        if usuario is None:
            raise UsuarioNoEncontrado()

        try:
            codigo_sanitizado = validar_codigo_comportamiento(codigo)
        except CodigoComportamientoInvalido as exc:
            raise DatosInvalidos() from exc

        nuevo_comportamiento = ComportamientoModelo(id_usuario = usuario_id, nombre= nombre.strip(), codigo= codigo_sanitizado)
        comportamiento = self.comportamientos.crear(nuevo_comportamiento)

        return CrearComportamientoResultado(comportamiento=comportamiento)
    
    def unirse_liga(self, liga_id: int, usuario_id: int, jugadores_comportamientos: list[tuple[int, int]], formacion: Formacion, contraseña: str | None = None) -> UnirseLigaResultado:
        
        liga = self.ligas.obtener_por_id(liga_id)

        if liga is None:
            raise LigaNoEncontrada()

        if liga.estado != EstadoLiga.DISPONIBLE:
            raise LigaNoDisponible()

        if len(liga.participantes) >= liga.max_jugadores:
            raise LigaLlena()

        if liga.contraseña is not None and liga.contraseña.strip() != "":
            if contraseña != liga.contraseña:
                raise ContraseñaLigaIncorrecta()

        usuario = self.usuarios.obtener_por_id(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado()

        if any(u.id_usuario == usuario_id for u in liga.participantes):
            raise UsuarioYaEnLiga()
        
        if liga.id_usuario == usuario_id:
            raise UsuarioEsCreadorDeLiga()

        if self.jugadores.contar_jugadores_usuario(usuario_id) < 6:
            raise JugadoresInsuficientes()
        
        if len(jugadores_comportamientos) != 6:
            raise DatosInvalidos()
        
        id_jugadores = [id_jugador for id_jugador, _ in jugadores_comportamientos]
        if len(set(id_jugadores)) != 6:
            raise DatosInvalidos()
        
        jugadores = []
        for id_jugador, id_comportamiento in jugadores_comportamientos:
            jugador = self.jugadores.obtener_por_id(id_jugador)

            if jugador is None or jugador.id_usuario != usuario_id:
                raise JugadorNoEncontrado()
            
            comportamiento = self.comportamientos.obtener_comportamiento_por_id_y_usuario(id_comportamiento, usuario_id)
            if comportamiento is None:
                raise ComportamientoNoEncontrado()
            
            jugadores.append((jugador, id_comportamiento))

        resultado_equipo = self.crear_equipo(usuario_id=usuario_id)
        equipo = resultado_equipo.equipo
        for indice, (jugador, id_comportamiento) in enumerate(jugadores):
            estado = (EstadoJugador.TITULAR if indice < 3 else EstadoJugador.SUPLENTE)
            self.agregar_jugador_a_equipo(
                usuario_id=usuario_id, id_equipo=equipo.id_equipo, id_jugador=jugador.id_jugador,
                id_comportamiento=id_comportamiento, estado=estado
            ) # el for es para agregar los jugadores al equipo del usuario que crea la liga

        participacion = self.ligas.agregar_participante(liga, usuario, equipo.id_equipo, formacion)
        return UnirseLigaResultado(liga=liga, usuario_unido=usuario, participacion=participacion)
    
    def abandonar_liga(self, liga_id: int, usuario_id: int) -> AbandonarLigaResultado:
        liga = self.ligas.obtener_por_id(liga_id)

        if liga is None:
            raise LigaNoEncontrada()

        usuario = self.usuarios.obtener_por_id(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado()

        if not any(u.id_usuario == usuario_id for u in liga.participantes):
            raise UsuarioNoExisteEnLiga()
        
        if liga.estado != EstadoLiga.DISPONIBLE:
            raise LigaIniciada()


        liga_actualizada = self.ligas.eliminar_participante(liga, usuario)

        return AbandonarLigaResultado(liga=liga_actualizada, usuario_abandonado=usuario)

    def listar_ligas_disponibles(self) -> ListarLigasResultado:
        ligas = self.ligas.obtener_ligas_disponibles()
        return ListarLigasResultado(ligas=ligas)


    def iniciar_liga(self, id_liga: int, usuario_id: int) -> IniciarLigaResultado:
        liga = self.ligas.obtener_por_id(id_liga)

        if liga is None:
            raise LigaNoEncontrada()

        if liga.id_usuario != usuario_id:
            raise IniciarNoPermitido()

        if liga.estado != EstadoLiga.DISPONIBLE:
            raise NoEsPosibleIniciarLiga()
        
        participantes = self.ligas.obtener_participantes_liga(id_liga)
        cantidad_participantes = len(participantes)

        if cantidad_participantes < liga.min_jugadores:
            raise NoEsPosibleIniciarLiga()
        
        if cantidad_participantes > liga.max_jugadores:
            raise NoEsPosibleIniciarLiga()
        
        tabla = []

        for participante in participantes:
            registro = TablaLiga(
                id_liga=liga.id,
                id_equipo=participante.id_equipo,
                id_usuario=participante.id_usuario,
                partidos_ganados=0,
                partidos_empatados=0,
                partidos_perdidos=0,
                puntos=0,
                goles_a_favor=0,
                goles_en_contra=0)

            tabla.append(registro)

        enfrentamientos = list(combinations(participantes, 2))
        random.shuffle(enfrentamientos)

        fixture = []
        for turno, (equipo1, equipo2) in enumerate(enfrentamientos, start=1):
            partido_fixture = FixtureLiga(
                id_liga=liga.id,
                id_equipo_izq=equipo1.id_equipo,
                id_equipo_der=equipo2.id_equipo,
                turno=turno)

            fixture.append(partido_fixture)

        equipo1, equipo2 = enfrentamientos[0]

        nuevo_partido = PartidoModelo(
            id_usuario_1=equipo1.id_usuario,
            id_usuario_2=equipo2.id_usuario,
            id_equipo_1=equipo1.id_equipo,
            id_equipo_2=equipo2.id_equipo,
            duracion_partido=liga.duracion_partido,
            formacion_1=equipo1.formacion,
            formacion_2=equipo2.formacion,
            tipo_partido=TipoPartido.LIGA,
            estado_partido=EstadoPartido.EN_CURSO)

        partido = self.partidos.crear(nuevo_partido)

        self.ligas.asignar_partido_fixture(fixture=fixture[0], partido_id=partido.id_partido)
        self.ligas.guardar_inicio_liga(liga=liga, tabla=tabla, fixture=fixture)

        return IniciarLigaResultado(liga=liga, partido=partido, fixture=fixture, tabla=tabla)
    

    def crear_siguiente_partido_liga(self, id_liga: int) -> CrearPartidoResultado:
        liga = self.ligas.obtener_por_id(id_liga)

        if liga is None:
            raise LigaNoEncontrada()

        fixture = self.ligas.obtener_siguiente_fixture(id_liga)

        if fixture is None:
            return CrearPartidoResultado(partido=None)

        equipo1 = self.ligas.obtener_participante_por_equipo(id_liga, fixture.id_equipo_izq)
        equipo2 = self.ligas.obtener_participante_por_equipo(id_liga, fixture.id_equipo_der)

        if equipo1 is None or equipo2 is None:
            raise NoEsPosibleIniciarLiga()

        nuevo_partido = PartidoModelo(
            id_usuario_1=equipo1.id_usuario,
            id_usuario_2=equipo2.id_usuario,
            id_equipo_1=equipo1.id_equipo,
            id_equipo_2=equipo2.id_equipo,
            duracion_partido=liga.duracion_partido,
            formacion_1=equipo1.formacion,
            formacion_2=equipo2.formacion,
            tipo_partido=TipoPartido.LIGA,
            estado_partido=EstadoPartido.EN_CURSO)

        partido = self.partidos.crear(nuevo_partido)

        self.ligas.asignar_partido_fixture(fixture=fixture, partido_id=partido.id_partido)
        self.ligas.actualizar()

        return CrearPartidoResultado(partido=partido)
    

    def registrar_resultado_partido_liga(self, id_liga: int, turno: int, goles_izq: int, goles_der: int) -> RegistrarResultadoPartidoLiga:
        fixture = self.ligas.obtener_fixture_por_turno(id_liga, turno)

        tabla_izq = self.ligas.obtener_registro_tabla(id_liga, fixture.id_equipo_izq)
        tabla_der = self.ligas.obtener_registro_tabla(id_liga, fixture.id_equipo_der)

        partido = self.partidos.obtener_por_id(fixture.id_partido)

        if partido is None:
            raise PartidoNoEncontrado()

        if tabla_izq is None or tabla_der is None:
            raise NoSeEncontraronLasTablas()

        # guardo los goles en el fixture
        fixture.goles_equipo_izq = goles_izq
        fixture.goles_equipo_der = goles_der

        # actualizo los goles de ambos equipos
        tabla_izq.goles_a_favor += goles_izq
        tabla_izq.goles_en_contra += goles_der

        tabla_der.goles_a_favor += goles_der
        tabla_der.goles_en_contra += goles_izq

        # actualizo el resultado del partido
        if goles_izq > goles_der:
            tabla_izq.partidos_ganados += 1
            tabla_izq.puntos += 3
            tabla_der.partidos_perdidos += 1

        elif goles_der > goles_izq:
            tabla_der.partidos_ganados += 1
            tabla_der.puntos += 3
            tabla_izq.partidos_perdidos += 1

        else:
            tabla_izq.partidos_empatados += 1
            tabla_der.partidos_empatados += 1
            tabla_izq.puntos += 1
            tabla_der.puntos += 1

        self.ligas.actualizar()

        return RegistrarResultadoPartidoLiga(fixture=fixture, tabla_izq=tabla_izq, tabla_der=tabla_der)
    
    def finalizar_liga(self, id_liga: int):
        liga = self.ligas.obtener_por_id(id_liga)

        if liga is None:
            raise LigaNoEncontrada()

        liga_finalizada = self.ligas.finalizar_liga(liga)
        
        return FinalizarLigaResultado(liga=liga_finalizada)

      
    def editar_comportamiento(self, usuario_id: int, comp_id: int, nombre: str, codigo: str) -> EditarComportamientoResultado:
        if not nombre.strip():
            raise DatosInvalidos()

        if len(nombre.strip()) > 50:
            raise DatosInvalidos()

        comportamiento = self.comportamientos.obtener_comportamiento_por_id_y_usuario(comp_id, usuario_id)

        if comportamiento is None:
            raise ComportamientoNoEncontrado()

        if (comportamiento.nombre, comportamiento.codigo) in COMPORTAMIENTOS_PREDETERMINADOS:
            raise ComportamientoNoEditable()

        try:
            codigo_sanitizado = validar_codigo_comportamiento(codigo)
        except CodigoComportamientoInvalido as exc:
            raise DatosInvalidos() from exc

        comportamiento.nombre = nombre.strip()
        comportamiento.codigo = codigo_sanitizado

        comportamiento = self.comportamientos.actualizar(comportamiento)

        return EditarComportamientoResultado(comportamiento=comportamiento)

    def eliminar_comportamiento(self, usuario_id: int, comp_id: int) -> None:
        comportamiento = self.comportamientos.obtener_comportamiento_por_id_y_usuario(comp_id, usuario_id)

        if comportamiento is None:
            raise ComportamientoNoEncontrado()

        if (comportamiento.nombre, comportamiento.codigo) in COMPORTAMIENTOS_PREDETERMINADOS:
            raise ComportamientoNoEditable()
        
        if (comportamiento.equipos_jugadores):
            raise ComportamientoEnUso()
        
        self.comportamientos.eliminar(comportamiento)

    def obtener_fixture(self, liga_id: int) -> FixtureCompletoResultado:
        liga = self.ligas.obtener_por_id(liga_id)

        if liga is None:
            raise LigaNoEncontrada()

        if liga.estado != EstadoLiga.EN_JUEGO:
            raise NoEsPosibleVerElFixture()
        
        fixture = self.ligas.obtener_fixture_completo(liga_id)

        if not fixture:
            raise NoEsPosibleVerElFixture()
        
        return FixtureCompletoResultado(fixture=fixture)
    
    def obtener_tabla(self, liga_id: int) -> TablaCompletaResultado:
        liga = self.ligas.obtener_por_id(liga_id)

        if liga is None:
            raise LigaNoEncontrada()

        if liga.estado != EstadoLiga.EN_JUEGO:
            raise NoEsPosibleVerLaTabla()
        
        tabla = self.ligas.obtener_tabla_completa(liga_id)

        if not tabla:
            raise NoEsPosibleVerLaTabla()
        
        return TablaCompletaResultado(tabla=tabla)
    
    def obtener_datos_cambio_jugador(self, partido_id: int, usuario_id: int, jugador_sale_id: int, jugador_entra_id: int) -> CambioJugadorResultado:
        partido = self.partidos.obtener_por_id(partido_id)

        if partido is None:
            raise PartidoNoEncontrado()
        
        if partido.id_usuario_1 == usuario_id:
            id_equipo = partido.id_equipo_1

        elif partido.id_usuario_2 == usuario_id:
            id_equipo = partido.id_equipo_2

        else:
            raise UsuarioNoEncontrado
        
        if jugador_sale_id == jugador_entra_id:
            raise NoSePuedeCambiarJugador
        

        jugador_sale = self.equipos.obtener_jugador_equipo(id_equipo, jugador_sale_id)

        if jugador_sale is None:
            raise JugadorNoEncontrado
             
        jugador_entra = self.equipos.obtener_jugador_equipo(id_equipo, jugador_entra_id)

        if jugador_entra is None:
            raise JugadorNoEncontrado
        
        
        jugador = jugador_entra.jugador
        comportamiento = jugador_entra.comportamiento

        
        return CambioJugadorResultado(
            id_jugador=jugador.id_jugador,
            control=jugador.control,
            agilidad=jugador.agilidad,
            fuerza=jugador.fuerza,
            poder=jugador.poder,
            velocidad=jugador.velocidad,
            codigo_comportamiento=comportamiento.codigo)

    def obtener_equipo_de_liga(self, id_liga: int, id_equipo: int) -> EquipoLigaResultado:
            liga = self.ligas.obtener_por_id(id_liga)
            if liga is None:
                raise LigaNoEncontrada()
    
            participacion = self.ligas.obtener_participante_por_equipo(id_liga, id_equipo)
            if participacion is None:
                raise EquipoNoEncontrado()
    
            equipo = self.equipos.obtener_por_id(id_equipo)
            if equipo is None:
                raise EquipoNoEncontrado()
    
            return EquipoLigaResultado(equipo=equipo, participacion=participacion)
    
    def obtener_datos_cambio_comportamiento(self, partido_id: int, usuario_id: int, jugador_id: int, comportamiento_id: int) -> CambioComportamientoResultado:
        partido = self.partidos.obtener_por_id(partido_id)

        if partido is None:
            raise PartidoNoEncontrado()

        if partido.id_usuario_1 == usuario_id:
            id_equipo = partido.id_equipo_1

        elif partido.id_usuario_2 == usuario_id:
            id_equipo = partido.id_equipo_2

        else:
            raise UsuarioNoEncontrado()

        jugador_equipo = self.equipos.obtener_jugador_equipo(id_equipo, jugador_id)

        if jugador_equipo is None:
            raise JugadorNoEncontrado()

        comportamiento = self.comportamientos.obtener_comportamiento_por_id_y_usuario(comportamiento_id, usuario_id)

        if comportamiento is None:
            raise ComportamientoNoEncontrado()

        return CambioComportamientoResultado(jugador_id=jugador_equipo.id_jugador, codigo_comportamiento=comportamiento.codigo, nombre_comportamiento=comportamiento.nombre)