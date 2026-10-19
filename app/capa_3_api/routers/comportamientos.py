from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import *
from app.capa_3_api.dependencias import obtener_servicio
from app.capa_3_api.dtos.comportamientos import CrearComportamiento

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
    
@comportamiento_router.get("/comportamientos/{usuario_id}")
def obtener_comportamientos_usuario(usuario_id: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.listar_comportamientos(usuario_id)

        return [
            {
                "id": comportamiento.id,
                "nombre": comportamiento.nombre,
                "codigo": comportamiento.codigo
            }
            for comportamiento in resultado.comportamientos
        ]

    except ComportamientosNoEncontrados:
        return JSONResponse(status_code=404, content={"error": "COMPORTAMIENTOS_NO_ENCONTRADOS", "mensaje": "No hay comportamientos disponibles"})
    
    except Exception:
        return JSONResponse(status_code=500, content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"})

@comportamiento_router.post("/comportamiento/{usuario_id}", status_code=status.HTTP_201_CREATED)
def crear_comportamiento(usuario_id: int, datos: CrearComportamiento, servicio: Servicios= Depends(obtener_servicio)):
    try:
        resultado = servicio.crear_comportamiento(usuario_id=usuario_id, nombre=datos.nombre, codigo=datos.codigo)
        comp = resultado.comportamiento

        return {
            "id": comp.id,
            "id_usuario": comp.id_usuario,
            "nombre": comp.nombre,
            "codigo": comp.codigo,
        }

    except DatosInvalidos:
        return JSONResponse(
            status_code=400,
            content={
                "error": "DATOS_INVALIDOS",
                "mensaje": "El nombre o los datos del comportamiento no son validos",
            }
        )
    except UsuarioNoEncontrado:
        return JSONResponse(
                status_code=404,
                content={
                    "error": "USUARIO_NO_ENCONTRADO",
                    "mensaje": "El usaurio no existe",
                }
            )
    except Exception:
        return JSONResponse(
                status_code=500,
                content={
                    "error": "ERROR_INTERNO",
                    "mensaje": "Ocurrio un error interno del servidor",
                }
            )