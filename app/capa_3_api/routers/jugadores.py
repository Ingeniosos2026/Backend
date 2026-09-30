from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import DatosInvalidos
from app.capa_3_api.dtos.jugadores import CrearJugador
from app.capa_3_api.dependencias import obtener_servicio

jugador_router = APIRouter()

@jugador_router.post("/jugador/{usuario_id}", status_code=status.HTTP_201_CREATED)
def crear_jugador(usuario_id: int, datos: CrearJugador, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.crear_jugador(
            usuario_id=usuario_id,
            nombre=datos.nombre,
            power=datos.power,
            agility=datos.agility,
            control=datos.control,
            speed=datos.speed,
            strength=datos.strength
        )
        jugador_bd = resultado.jugador
        
        return {
            "id": jugador_bd.id_jugador,
            "nombre": jugador_bd.nombre_jugador,
            "power": jugador_bd.poder,
            "agility": jugador_bd.agilidad,
            "control": jugador_bd.control,
            "speed": jugador_bd.velocidad,
            "strength": jugador_bd.fuerza
        }
        
    except DatosInvalidos:
        return JSONResponse(
            status_code=400, 
            content={
                "error": "DATOS_INVALIDOS", 
                "mensaje": "Las estadisticas no pueden ser mayores a 100 ni menores a 20 y el total debe ser menor o igual a 300"
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