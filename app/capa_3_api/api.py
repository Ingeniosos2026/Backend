from fastapi import APIRouter
from .routers.usuarios import usuario_router
from .routers.jugadores import jugador_router
from .routers.partidos import partido_router
from .routers.equipos import equipo_router
from .routers.comportamientos import comportamiento_router

api_router = APIRouter()
api_router.include_router(usuario_router)
api_router.include_router(jugador_router)
api_router.include_router(partido_router)
api_router.include_router(equipo_router)
api_router.include_router(comportamiento_router)