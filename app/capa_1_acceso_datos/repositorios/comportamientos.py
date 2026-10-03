from typing import List
from sqlalchemy.orm import Session
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento as ComportamientoModelo

class ComportamientoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def obtener_comportamiento_por_id_y_usuario(self, comp_id: int, usuario_id: int) -> ComportamientoModelo | None:
        return (
            self.db.query(ComportamientoModelo)
            .filter(ComportamientoModelo.id == comp_id, ComportamientoModelo.id_usuario == usuario_id)
            .first()
        )
    

    def obtener_comportamientos_usuario(self, usuario_id: int) -> List[ComportamientoModelo]:
        return (self.db.query(ComportamientoModelo).filter(ComportamientoModelo.id_usuario == usuario_id).all())