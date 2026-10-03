from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import *
from app.capa_3_api.dtos.partidos import CrearAmistoso
from app.capa_3_api.dependencias import obtener_servicio

partido_router = APIRouter()

@partido_router.post("/partido/{usuario_id}", status_code=status.HTTP_201_CREATED)
def crear_amistoso(usuario_id: int, datos: CrearAmistoso, servicio: Servicios = Depends(obtener_servicio)):
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
        
        return {
            "id_partido": partido_bd.id_partido,
            "id_usuario_1": partido_bd.id_usuario_1,
            "id_usuario_2": partido_bd.id_usuario_2,
            "id_equipo_1": partido_bd.id_equipo_1,
            "id_equipo_2": partido_bd.id_equipo_2,
            "duracion": partido_bd.duracion_partido,
            "formacion": partido_bd.formacion,
            "tipo": partido_bd.tipo_partido.name,
            "estado": partido_bd.estado_partido.name
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