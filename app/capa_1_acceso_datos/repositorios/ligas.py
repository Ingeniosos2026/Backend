from sqlalchemy.orm import Session

from app.capa_0_definicion_bd.models.liga_modelos import Liga as LigaModelo


class LigaRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, liga: LigaModelo) -> LigaModelo:
        self.db.add(liga)
        self.db.commit()
        self.db.refresh(liga)
        return liga