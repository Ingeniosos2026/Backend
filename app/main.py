from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base, engine
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario

app = FastAPI()

origins = [
    "http://localhost:5173"
]

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