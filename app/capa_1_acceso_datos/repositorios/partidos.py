from sqlalchemy.orm import Session
from app.capa_0_definicion_bd.models.partidos_modelos import Partido as PartidoModelo

class PartidoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, partido: PartidoModelo) -> PartidoModelo:
        self.db.add(partido)
        self.db.flush()
        self.db.refresh(partido)
        return partido
