from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import *
from app.capa_3_api.dependencias import obtener_servicio

equipo_router = APIRouter()

@equipo_router.post("/equipo/{usuario_id}", status_code=status.HTTP_201_CREATED)
def crear_equipo(usuario_id: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.crear_equipo(usuario_id=usuario_id)
        equipo_bd = resultado.equipo
        
        return {
            "id_equipo": equipo_bd.id_equipo,
            "id_usuario": equipo_bd.id_usuario
        }

# este caso realmente puede pasar? esta mas que nada para probarlo en swagger
    except UsuarioNoEncontrado:
        return JSONResponse(
            status_code=404, 
            content={"error": "USUARIO_NO_ENCONTRADO", "mensaje": "El usuario no existe"}
        )
    except Exception:
        return JSONResponse(
            status_code=500, 
            content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"}
        )

@equipo_router.post("/equipo/{usuario_id}/{id_equipo}/jugador/{id_jugador}", status_code=status.HTTP_201_CREATED)
def agregar_jugador_a_equipo(usuario_id: int, id_equipo: int, id_jugador: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.agregar_jugador_a_equipo(usuario_id=usuario_id, id_equipo=id_equipo, id_jugador=id_jugador)
        equipo_bd = resultado.equipo
        
        return {
            "id_equipo": equipo_bd.id_equipo,
            "id_jugador": id_jugador
        }
    except UsuarioNoEncontrado:
        return JSONResponse(
            status_code=404, 
            content={"error": "USUARIO_NO_ENCONTRADO", "mensaje": "El usuario no existe"}
        )
    except EquipoNoEncontrado:
        return JSONResponse(
            status_code=404, 
            content={"error": "EQUIPO_NO_ENCONTRADO", "mensaje": "El equipo no existe"}
        )
    except JugadorNoEncontrado:
        return JSONResponse(
            status_code=404, 
            content={"error": "JUGADOR_NO_ENCONTRADO", "mensaje": "El jugador no existe"}
        )
    except Exception:
        return JSONResponse(
            status_code=500, 
            content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"}
        )