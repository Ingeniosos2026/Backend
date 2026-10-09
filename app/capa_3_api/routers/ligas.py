from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import DatosInvalidos, UsuarioNoEncontrado
from app.capa_3_api.dtos.ligas import CrearLiga
from app.capa_3_api.dependencias import obtener_servicio

liga_router = APIRouter()


@liga_router.post("/liga/{usuario_id}", status_code=status.HTTP_201_CREATED)
def crear_liga(usuario_id: int, datos: CrearLiga, servicio: Servicios = Depends(obtener_servicio)):
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