from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional
import asyncio

from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import *
from app.capa_3_api.dtos.ligas import CrearLiga, UnirseLiga
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones
from app.capa_3_api.dependencias import obtener_servicio
from app.partido.administrar_partidos import administrador_partidas
from app.partido.inicializacion import crear_estado_partido, crear_cancha
from app.partido.motor import MotorPartido
from app.partido.ejecutorliga import EjecutorLiga
from app.partido.convertidor import tabla_a_dict, fixture_a_dict

liga_router = APIRouter()


@liga_router.post("/liga/{usuario_id}", status_code=status.HTTP_201_CREATED)
async def crear_liga(usuario_id: int, datos: CrearLiga, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.crear_liga(
            usuario_id=usuario_id,
            nombre=datos.nombre,
            contraseña=datos.contraseña,
            min_jugadores=datos.min_jugadores,
            max_jugadores=datos.max_jugadores,
            duracion_partido=datos.duracion_partido,
            jugadores_comportamientos=[(j.id_jugador, j.id_comportamiento) for j in datos.jugadores],
            formacion=datos.formacion
        )

        liga = resultado.liga
        participacion = resultado.participacion
        await admin_conexiones.difundir("liga creada",
            {
                "id_liga": liga.id,
                "duracion": liga.duracion_partido,
                "nombre": liga.nombre,
                "min_jugadores": liga.min_jugadores,
                "max_jugadores": liga.max_jugadores,
            })

        return {
            "id": liga.id,
            "id_usuario": liga.id_usuario,
            "nombre": liga.nombre,
            "min_jugadores": liga.min_jugadores,
            "max_jugadores": liga.max_jugadores,
            "duracion_partido": liga.duracion_partido,
            "estado": liga.estado.name,
            "id_equipo": participacion.id_equipo,
            "formacion": participacion.formacion.value
        }

    except DatosInvalidos:
        return JSONResponse(
            status_code=400,
            content={"error": "DATOS_INVALIDOS","mensaje": "Los datos de la liga no son válidos"}
        )

    except UsuarioNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={"error": "USUARIO_NO_ENCONTRADO", "mensaje": "El usuario no existe"}
        )
    
    except JugadoresInsuficientes:
        return JSONResponse(
            status_code=400,
            content={"error": "JUGADORES_INSUFICIENTES", "mensaje": "Tenes que tener al menos 6 jugadores"},
        )
    
    except ComportamientoNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={"error": "COMPORTAMIENTO_NO_ENCONTRADO", "mensaje": "El jugador no tiene un comportamiento válido"},
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"}
        )
    
@liga_router.put("/liga/{liga_id}/unirse/{usuario_id}", status_code=status.HTTP_200_OK)
async def unirse_liga(liga_id: int,usuario_id: int, datos: UnirseLiga, servicio: Servicios = Depends(obtener_servicio)):
    try:
        contraseña = datos.contraseña if datos else None

        resultado = servicio.unirse_liga(
            liga_id=liga_id, 
            usuario_id=usuario_id, 
            contraseña=contraseña,
            jugadores_comportamientos=[(j.id_jugador, j.id_comportamiento) for j in datos.jugadores],
            formacion=datos.formacion
        )

        participacion = resultado.participacion

        await admin_conexiones.emitir_lobby_liga(
            liga_id=liga_id,
            accion="usuario_unido_liga",
            payload={
                "usuario_unido": {
                    "id": resultado.usuario_unido.id_usuario,
                    "nombre": resultado.usuario_unido.nombre,
                    "club": resultado.usuario_unido.nombre_club,
                    "id_equipo": participacion.id_equipo,
                    "formacion": participacion.formacion.value
                }
            }
        )

        return {
            "id_liga": resultado.liga.id,
            "id_usuario": resultado.usuario_unido.id_usuario,
            "id_equipo": participacion.id_equipo,
            "formacion": participacion.formacion.value
        }
    except LigaNoEncontrada:
        return JSONResponse(
            status_code=404, 
            content={"error": "LIGA_NO_ENCONTRADA", "mensaje": "La liga no existe"})
    
    except LigaNoDisponible:
        return JSONResponse(
            status_code=409, 
            content={"error": "LIGA_NO_DISPONIBLE", "mensaje": "La liga no está disponible"})
    
    except LigaLlena:
        return JSONResponse(
            status_code=409, 
            content={"error": "LIGA_LLENA", "mensaje": "La liga alcanzo su maximo de jugadores"})
    
    except UsuarioYaEnLiga:
        return JSONResponse(
            status_code=409, 
            content={"error": "USUARIO_YA_EN_LIGA", "mensaje": "Ya perteneces a esta liga"})
    
    except ContraseñaLigaIncorrecta:
        return JSONResponse(
            status_code=401, 
            content={"error": "CONTRASEÑA_INCORRECTA", "mensaje": "Contraseña incorrecta"})
    
    except JugadoresInsuficientes:
        return JSONResponse(
            status_code=400, 
            content={"error": "JUGADORES_INSUFICIENTES", "mensaje": "Tenes que tener al menos 6 jugadores"})
    
    except UsuarioNoEncontrado:
        return JSONResponse(
            status_code=404, 
            content={"error": "USUARIO_NO_ENCONTRADO", "mensaje": "El usuario no existe"})
    
    except UsuarioEsCreadorDeLiga:
        return JSONResponse(
            status_code= 400, 
            content={"error": "USUARIO_ES_CREADOR_DE_LIGA", "mensaje": "El creador de la liga no puede unirse a su propia liga"})
    
    except ComportamientoNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={"error": "COMPORTAMIENTO_NO_ENCONTRADO", "mensaje": "El jugador no tiene un comportamiento válido"},
        )
            
    except Exception:
        return JSONResponse(
            status_code=500, 
            content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno"})

@liga_router.put("/liga/{liga_id}/abandonar/{usuario_id}", status_code=status.HTTP_200_OK)    
async def abandonar_liga(liga_id: int, usuario_id: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.abandonar_liga(
            liga_id=liga_id, 
            usuario_id=usuario_id
        )

        await admin_conexiones.emitir_lobby_liga(
            liga_id=liga_id,
            accion="usuario_abandono_liga",
            payload={
                "usuario_abandono": {
                    "id": resultado.usuario_abandonado.id_usuario,
                    "nombre": resultado.usuario_abandonado.nombre,
                    "club": resultado.usuario_abandonado.nombre_club
                }
            }
        )

        return {
            "id_liga": resultado.liga.id,
            "id_usuario": resultado.usuario_abandonado.id_usuario,
        }

    except LigaNoEncontrada:
        return JSONResponse(
            status_code=404, 
            content={"error": "LIGA_NO_ENCONTRADA", "mensaje": "La liga no existe"})
    
    except UsuarioNoExisteEnLiga:
        return JSONResponse(
            status_code=404, 
            content={"error": "USUARIO_NO_EXISTE_EN_LIGA", "mensaje": "El usuario no pertenece a esta liga"})
    
    except LigaIniciada:
        return JSONResponse(
            status_code=409, 
            content={"error": "LIGA_INICIADA", "mensaje": "No se puede abandonar una liga que ya ha iniciado"})

    except Exception:
        return JSONResponse(
            status_code=500, 
            content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"})
@liga_router.get("/ligas", status_code=status.HTTP_200_OK)
def listar_ligas(servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.listar_ligas_disponibles()

        return [
            {
                "id_liga": liga.id,
                "id_usuario": liga.id_usuario,
                "nombre": liga.nombre,
                "estado": liga.estado.value,
                "min_jugadores": liga.min_jugadores,
                "max_jugadores": liga.max_jugadores,
                "duracion_partido": liga.duracion_partido,
                "es_privada": bool(liga.contraseña)
            }
            for liga in resultado.ligas
        ]

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "error": "ERROR_INTERNO",
                "mensaje": "Ocurrió un error interno del servidor",
            },
        )

@liga_router.put("/liga/{liga_id}/{usuario_id}", status_code=status.HTTP_200_OK)
async def iniciar_liga(liga_id: int, usuario_id: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.iniciar_liga(id_liga=liga_id, usuario_id=usuario_id)

        partido = resultado.partido
        estado = crear_estado_partido(partido)
        duracion_segundos = partido.duracion_partido * 60
        motor = MotorPartido(estado=estado)
        administrador_partidas.agregar(partido_id=partido.id_partido, motor=motor)

        fixture = [fixture_a_dict(fix) for fix in resultado.fixture]
        tabla = [tabla_a_dict(tab) for tab in resultado.tabla]

        ejecutor = EjecutorLiga(liga_id=liga_id, partido_id=partido.id_partido, motor=motor, duracion=duracion_segundos, turno=1)
        asyncio.create_task(ejecutor.ejecutar())

    except LigaNoEncontrada:
        return JSONResponse(status_code=404, content={"error": "LIGA_NO_ENCONTRADA", "mensaje": "La liga no existe"})

    except IniciarNoPermitido:
        return JSONResponse(status_code=403, content={"error": "INICIAR_NO_PERMITIDO", "mensaje": "No se puede iniciar una liga que no creaste"})

    except NoEsPosibleIniciarLiga:
        return JSONResponse(status_code=409, content={"error": "LIGA_NO_PUEDE_INICIAR", "mensaje": "La liga no puede iniciarse en su estado actual"})

    except Exception:
        return JSONResponse(status_code=500, content={"error": "ERROR_INTERNO", "mensaje": "No se pudo iniciar la liga"})

    await admin_conexiones.emitir_lobby_liga(
        liga_id=liga_id,
        accion="liga_iniciada",
        payload={
            "accion": "primer_partido_iniciado",
            "estado": "EN_JUEGO",
            "id_partido_actual": partido.id_partido,
            "fixture": fixture,
            "tabla": tabla,
            "turno": 1})

    return {
        "mensaje": "Liga iniciada",
        "id_liga": liga_id,
        "id_partido": partido.id_partido}


@liga_router.get("/liga/{liga_id}/fixture", status_code=status.HTTP_200_OK)
async def fixture(liga_id: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.obtener_fixture(liga_id=liga_id)
        fixture = [fixture_a_dict(fix) for fix in resultado.fixture]
    
        return {"fixture": fixture}
    
    except LigaNoEncontrada:
        return JSONResponse(status_code=404, content={"error": "LIGA_NO_ENCONTRADA", "mensaje": "La liga no existe"})

    except NoEsPosibleVerElFixture:
        return JSONResponse(status_code=409, content={"error": "LIGA_NO_DISPONIBLE", "mensaje": "La liga esta finalizada o no esta iniciada"})

    except Exception:
        return JSONResponse(status_code=500, content={"error": "ERROR_INTERNO", "mensaje": "No se pudo obtener el fixture de la liga"})
    

@liga_router.get("/liga/{liga_id}/tabla", status_code=status.HTTP_200_OK)
async def tabla(liga_id: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.obtener_tabla(liga_id=liga_id)
        tabla = [tabla_a_dict(tab) for tab in resultado.tabla]

        return {"tabla": tabla}

    except LigaNoEncontrada:
        return JSONResponse(status_code=404, content={"error": "LIGA_NO_ENCONTRADA", "mensaje": "La liga no existe"})

    except NoEsPosibleVerLaTabla:
        return JSONResponse(status_code=409, content={"error": "LIGA_NO_DISPONIBLE", "mensaje": "La liga esta finalizada o no esta iniciada"})

    except Exception:
        return JSONResponse(status_code=500, content={"error": "ERROR_INTERNO", "mensaje": "No se pudo obtener la tabla de la liga"})