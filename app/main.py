from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base, engine
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento
from app.capa_0_definicion_bd.models.liga_modelos import Liga
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.equipos_jugadores_modelos import EquipoJugador
from app.capa_3_api.routers.websocket import ws_router
from app.capa_3_api.api import api_router

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175"
]

app.include_router(api_router)
app.include_router(ws_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"mensaje": "Backend funcionando"}