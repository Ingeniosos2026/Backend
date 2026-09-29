from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.capa_3_api.dtos.usuarios import *

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
            id_avatar=datos.id_avatar,
            contraseña=datos.contraseña,
            nombre_club=datos.nombre_club

        )

        usuario=resultado.usuario

        return {
            "mensaje": "Usuario creado",
            "id_usuario": usuario.id_usuario,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "id_avatar": usuario.id_avatar,
            "nombre_club": usuario.nombre_club
        }
    
    except EmailInvalido:
        raise HTTPException(status_code=400, detail="El email no es válido")

    except EmailRegistrado:
        raise HTTPException(status_code=400, detail="El email ya está registrado")