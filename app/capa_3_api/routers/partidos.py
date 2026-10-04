from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import *
from app.capa_3_api.dtos.partidos import CrearAmistoso, UnirseAmistoso
from app.capa_3_api.dependencias import obtener_servicio
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones

partido_router = APIRouter()

@partido_router.post("/partido/{usuario_id}", status_code=status.HTTP_201_CREATED)
def crear_amistoso(usuario_id: int, datos: CrearAmistoso, request: Request, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.crear_amistoso(
            usuario_id=usuario_id,
            jugadores_comportamientos=[
                (asignacion.id_jugador, asignacion.id_comportamiento)
                for asignacion in datos.jugadores
            ],
            duracion=datos.duracion,
            formacion=datos.formacion,
        )
        partido_bd = resultado.partido
        
        websocket_scheme = "wss" if request.url.scheme == "https" else "ws"
        websocket_url = request.url_for(
            "websocket_amistoso",
            partido_id=partido_bd.id_partido,
        ).replace(scheme=websocket_scheme)

        return {
            "id_partido": partido_bd.id_partido,
            "id_usuario_1": partido_bd.id_usuario_1,
            "id_usuario_2": partido_bd.id_usuario_2,
            "id_equipo_1": partido_bd.id_equipo_1,
            "id_equipo_2": partido_bd.id_equipo_2,
            "duracion": partido_bd.duracion_partido,
            "formacion": partido_bd.formacion,
            "tipo": partido_bd.tipo_partido.name,
            "estado": partido_bd.estado_partido.name,
            "websocket_url": str(websocket_url),
        }
    except DatosInvalidos:
        return JSONResponse(
            status_code=400, 
            content={"error": "DATOS_INVALIDOS", "mensaje": "La duracion del partido debe ser mayor a 0 y se deben seleccionar 6 jugadores distintos"}
        )    
    except EquipoNoEncontrado:
        return JSONResponse(
            status_code=404, 
            content={"error": "EQUIPO_NO_ENCONTRADO", "mensaje": "El equipo no existe"}
        )
    except JugadorNoEncontrado:
        return JSONResponse(
            status_code=404, 
            content={"error": "JUGADOR_NO_ENCONTRADO", "mensaje": "El jugador no existe o no pertenece al usuario"}
        )
    except ComportamientoNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={"error": "COMPORTAMIENTO_NO_ENCONTRADO", "mensaje": "El jugador no tiene un comportamiento válido"}
        )
    except Exception:
        return JSONResponse(
            status_code=500, 
            content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"}
        )


@partido_router.put("/partido/{partido_id}/unirse/{usuario_id}", status_code=status.HTTP_200_OK)
async def unirse_amistoso(partido_id: int, usuario_id: int, datos: UnirseAmistoso, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.unirse_amistoso(
            partido_id=partido_id,
            usuario_id=usuario_id,
            jugadores_comportamientos=[
                (asignacion.id_jugador, asignacion.id_comportamiento)
                for asignacion in datos.jugadores
            ],
        )
        partido_bd = resultado.partido

        await admin_conexiones.emitir_lobby(
            partido_id,
            "usuario_unido",
            {"usuario_id": usuario_id},
        )

        return {
            "id_partido": partido_bd.id_partido,
            "id_usuario_1": partido_bd.id_usuario_1,
            "id_usuario_2": partido_bd.id_usuario_2,
            "id_equipo_1": partido_bd.id_equipo_1,
            "id_equipo_2": partido_bd.id_equipo_2,
            "duracion": partido_bd.duracion_partido,
            "formacion": partido_bd.formacion,
            "tipo": partido_bd.tipo_partido.name,
            "estado": partido_bd.estado_partido.name,
        }
    except PartidoNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={"error": "PARTIDO_NO_ENCONTRADO", "mensaje": "El partido no existe"},
        )
    except PartidoNoDisponible:
        return JSONResponse(
            status_code=409,
            content={"error": "PARTIDO_NO_DISPONIBLE", "mensaje": "El partido ya no está disponible"},
        )
    except UsuarioNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={"error": "USUARIO_NO_ENCONTRADO", "mensaje": "El usuario no existe"},
        )
    except JugadoresInsuficientes:
        return JSONResponse(
            status_code=400,
            content={"error": "JUGADORES_INSUFICIENTES", "mensaje": "El usuario debe tener al menos 6 jugadores"},
        )
    except DatosInvalidos:
        return JSONResponse(
            status_code=400,
            content={"error": "DATOS_INVALIDOS", "mensaje": "Se deben seleccionar 6 jugadores distintos"},
        )
    except JugadorNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={"error": "JUGADOR_NO_ENCONTRADO", "mensaje": "El jugador no existe o no pertenece al usuario"},
        )
    except ComportamientoNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={"error": "COMPORTAMIENTO_NO_ENCONTRADO", "mensaje": "El jugador no tiene un comportamiento válido"},
        )
    
@partido_router.get("/partidos", status_code=status.HTTP_200_OK)
def listar_amistosos_disponibles(servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.listar_amistosos_disponibles()
        return [
            {
                "id": partido.id_partido,
                "nombre": f"Partido de {partido.usuario_1.nombre}",
            }
            for partido in resultado.amistosos
        ]
    except Exception:
        return JSONResponse(
            status_code=500, 
            content={
                "error": "ERROR_INTERNO", 
                "mensaje": "Ocurrió un error interno del servidor"
            }
        )