from fastapi import Depends 
from sqlalchemy.orm import Session
from app.capa_0_definicion_bd.base_datos_sqlalchemy import get_db
from app.capa_1_acceso_datos.repositorios.usuarios import UsuarioRepositorio
from app.capa_1_acceso_datos.repositorios.jugadores import JugadorRepositorio
from app.capa_1_acceso_datos.repositorios.comportamientos import ComportamientoRepositorio 
from app.capa_2_logica.servicios import Servicios 


def obtener_servicio(db: Session = Depends(get_db)) -> Servicios:
    repo_usuarios = UsuarioRepositorio(db) 
    repo_jugadores = JugadorRepositorio(db)
    repo_comportamientos = ComportamientoRepositorio(db)
    return Servicios(usuarios=repo_usuarios, jugadores=repo_jugadores, comportamientos=repo_comportamientos)
