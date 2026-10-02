from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import ComportamientoNoEncontrado
from app.capa_3_api.dependencias import obtener_servicio

comportamiento_router = APIRouter()

@comportamiento_router.get("/comportamiento/{usuario_id}/{comp_id}")
def ver_comportamiento(usuario_id: int, comp_id: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.obtener_comportamiento(usuario_id, comp_id)
        comp = resultado.comportamiento
        
        return {
            "id": comp.id,
            "nombre": comp.nombre,
            "codigo": comp.codigo
        }
        
    except ComportamientoNoEncontrado:
        return JSONResponse(
            status_code=404, 
            content={
                "error": "COMPORTAMIENTO_NO_ENCONTRADO", 
                "mensaje": "No existe el comportamiento"
            }
        )
    except Exception:
        return JSONResponse(
            status_code=500, 
            content={
                "error": "ERROR_INTERNO", 
                "mensaje": "Ocurrió un error interno del servidor"
            }
        )