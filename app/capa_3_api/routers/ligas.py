from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional

from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import DatosInvalidos, UsuarioNoEncontrado, UsuarioEsCreadorDeLiga ,LigaNoDisponible, LigaNoEncontrada, LigaLlena, UsuarioYaEnLiga, ContraseñaLigaIncorrecta, JugadoresInsuficientes
from app.capa_3_api.dtos.ligas import CrearLiga, UnirseLiga
from app.capa_3_api.websockets.admin_conexiones import admin_conexiones
from app.capa_3_api.dependencias import obtener_servicio

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
        )

        liga = resultado.liga

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

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"}
        )
    
@liga_router.put("/liga/{liga_id}/unirse/{usuario_id}", status_code=status.HTTP_200_OK)
async def unirse_liga(liga_id: int,usuario_id: int, datos: UnirseLiga | None = None, servicio: Servicios = Depends(obtener_servicio)):
    try:
        contraseña = datos.contraseña if datos else None

        resultado = servicio.unirse_liga(
            liga_id=liga_id, 
            usuario_id=usuario_id, 
            contraseña=contraseña
        )

        await admin_conexiones.emitir_lobby_liga(
            liga_id=liga_id,
            accion="usuario_unido_liga",
            payload={
                "usuario_unido": {
                    "id": resultado.usuario_unido.id_usuario,
                    "nombre": resultado.usuario_unido.nombre,
                    "club": resultado.usuario_unido.nombre_club
                }
            }
        )



        return {
            "id_liga": resultado.liga.id,
            "id_usuario": resultado.usuario_unido.id_usuario,
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
    
    except Exception:
        return JSONResponse(
            status_code=500, 
            content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno"})