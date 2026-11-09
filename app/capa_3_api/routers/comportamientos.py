from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import *
from app.capa_3_api.dependencias import obtener_servicio
from app.capa_3_api.dtos.comportamientos import CrearComportamiento, EditarComportamiento

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

@comportamiento_router.put("/comportamiento/{usuario_id}/{comp_id}")
def editar_comportamiento(usuario_id: int, comp_id: int, datos: EditarComportamiento, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.editar_comportamiento(
            usuario_id=usuario_id,
            comp_id=comp_id,
            nombre=datos.nombre,
            codigo=datos.codigo
        )

        comp = resultado.comportamiento

        return {
            "id": comp.id,
            "id_usuario": comp.id_usuario,
            "nombre": comp.nombre,
            "codigo": comp.codigo
        }

    except DatosInvalidos:
        return JSONResponse(
            status_code=400,
            content={
                "error": "DATOS_INVALIDOS",
                "mensaje": "El nombre o el código del comportamiento no son válidos"
            }
        )

    except ComportamientoNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={
                "error": "COMPORTAMIENTO_NO_ENCONTRADO",
                "mensaje": "No existe el comportamiento para este usuario"
            }
        )

    except ComportamientoNoEditable:
        return JSONResponse(
            status_code=403,
            content={
                "error": "COMPORTAMIENTO_NO_EDITABLE",
                "mensaje": "No se pueden editar los comportamientos predeterminados"
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

@comportamiento_router.delete("/comportamiento/{usuario_id}/{comp_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_comportamiento(usuario_id: int, comp_id: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        servicio.eliminar_comportamiento(usuario_id=usuario_id, comp_id=comp_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ComportamientoNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={
                "error": "COMPORTAMIENTO_NO_ENCONTRADO",
                "mensaje": "No existe el comportamiento para este usuario"
            }
        )

    except ComportamientoNoEditable:
        return JSONResponse(
            status_code=403,
            content={
                "error": "COMPORTAMIENTO_NO_EDITABLE",
                "mensaje": "No se pueden eliminar los comportamientos predeterminados"
            }
        )

    except ComportamientoEnUso:
        return JSONResponse(
            status_code=400,
            content={
                "error": "COMPORTAMIENTO_EN_USO",
                "mensaje": "No se puede eliminar un comportamiento que está en uso"
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

@comportamiento_router.get("/comportamientos_dt/{usuario_id}")
def obtener_comportamientos_dt(usuario_id: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.listar_comportamientos_dt(usuario_id)

        return {
            "comportamientos": [
                {
                    "id": comportamiento.id,
                    "nombre": comportamiento.nombre,
                    "codigo": comportamiento.codigo
                }
                for comportamiento in resultado.comportamientos
            ],
            "id_comportamiento_dt_actual": resultado.comportamiento_dt.id
        }

    except ComportamientosNoEncontrados:
        return JSONResponse(status_code=404, content={"error": "COMPORTAMIENTOS_NO_ENCONTRADOS", "mensaje": "No hay comportamientos DT disponibles"})
    
    except Exception:
        return JSONResponse(status_code=500, content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"})
    
@comportamiento_router.put("/comportamiento_dt/{usuario_id}/{comp_id}/dt/asignar", status_code=status.HTTP_200_OK)
def asignar_comportamiento_dt(usuario_id: int, comp_id: int, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.asignar_comportamiento_dt(
            usuario_id=usuario_id,
            id_comportamiento_dt=comp_id
        )
        return {
            "mensaje": "Comportamiento asignado al DT exitosamente",
            "id_usuario": resultado.usuario.id_usuario,
            "id_comportamiento_dt": resultado.usuario.id_comportamiento_dt,
            "nombre_comportamiento": resultado.comportamiento.nombre,
            "dt_activo": resultado.usuario.dt
        }
    
    except UsuarioNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={"error": "USUARIO_NO_ENCONTRADO", "mensaje": "El usuario no existe"}
        )
    except ComportamientoNoEncontrado:
        return JSONResponse(
            status_code=404,
            content={"error": "COMPORTAMIENTO_NO_ENCONTRADO", "mensaje": "El comportamiento no existe o no pertenece al usuario"}
        )
    except NoSePuedeAsignarComportamientoDTDefault:
        return JSONResponse(
            status_code=400,
            content={"error": "NO_SE_PUEDE_ASIGNAR_COMPORTAMIENTO_DT_DEFAULT", "mensaje": "No se puede asignar el comportamiento DT predeterminado"}
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"}
        )   