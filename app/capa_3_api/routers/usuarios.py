from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.capa_3_api.dtos.usuarios import *
from fastapi.responses import JSONResponse

from app.capa_2_logica.servicios import Servicios
from app.capa_2_logica.errores import *
from app.capa_3_api.dependencias import obtener_servicio



usuario_router = APIRouter()


@usuario_router.post("/usuario", status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: CrearUsuario, servicio: Servicios = Depends(obtener_servicio)):
    try:
        resultado = servicio.crear_usuario(
            email=datos.email,
            nombre=datos.nombre,
            id_avatar=datos.avatar,
            contraseña=datos.contraseña,
            nombre_club=datos.club
        )

        usuario=resultado.usuario

        return {
            "mensaje": "Usuario creado",
            "id": usuario.id_usuario,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "avatar": usuario.id_avatar,
            "club": usuario.nombre_club
        }

    except DatosInvalidos:
        return JSONResponse(status_code=400, content={"error": "DATOS_INVALIDOS", "mensaje": "Los datos enviados no son válidos"})
    
    except EmailRegistrado:
        return JSONResponse(status_code=409, content={"error": "USUARIO_YA_EXISTE", "mensaje": "Ya existe un usuario con esos datos"})
    
    except Exception:
        return JSONResponse(status_code=500, content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"})

@usuario_router.put("/usuario", status_code=status.HTTP_200_OK)
def login_usuario(datos: LoginUsuario, servicio: Servicios = Depends(obtener_servicio)):
    try:
        usuario = servicio.login_usuario(
            email=datos.email,
            contraseña=datos.contraseña
        )

        return {
            "mensaje": "Login exitoso",
            "id": usuario.id_usuario
        }

    except CredencialesInvalidas:
        return JSONResponse(status_code=401, content={"error": "CREDENCIALES_INVALIDAS", "mensaje": "El email o la contraseña son incorrectos"})
    
    except Exception:
        return JSONResponse(status_code=500, content={"error": "ERROR_INTERNO", "mensaje": "Ocurrió un error interno del servidor"})