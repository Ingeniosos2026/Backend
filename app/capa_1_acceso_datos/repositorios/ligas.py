from sqlalchemy.orm import Session

from app.capa_0_definicion_bd.models.liga_modelos import Liga as LigaModelo
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo


class LigaRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, liga: LigaModelo) -> LigaModelo:
        self.db.add(liga)
        self.db.commit()
        self.db.refresh(liga)
        return liga
    
    def obtener_por_id(self, id_liga: int) -> LigaModelo | None:
        return(self.db.query(LigaModelo)
        .filter(LigaModelo.id == id_liga)
        .first()
        )

    def agregar_participante(self, liga: LigaModelo, usuario: UsuarioModelo) -> LigaModelo:
        liga.participantes.append(usuario)
        self.db.commit()
        self.db.refresh(liga)
        return liga
    
