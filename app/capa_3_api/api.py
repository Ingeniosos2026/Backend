from fastapi import APIRouter
from .routers.usuarios import usuario_router
from .routers.jugadores import jugador_router

api_router = APIRouter()
api_router.include_router(usuario_router)
api_router.include_router(jugador_router)