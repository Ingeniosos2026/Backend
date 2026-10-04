from typing import List
from sqlalchemy.orm import Session
from app.capa_0_definicion_bd.models.partidos_modelos import Partido as PartidoModelo, TipoPartido, EstadoPartido

class PartidoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, partido: PartidoModelo) -> PartidoModelo:
        self.db.add(partido)
        self.db.commit()
        self.db.refresh(partido)
        return partido
    
    def obtener_partidos_amistosos_disponibles(self) -> List[PartidoModelo] | None:
        return (
            self.db.query(PartidoModelo) 
            .filter (
                PartidoModelo.tipo_partido == TipoPartido.AMISTOSO,
                PartidoModelo.estado_partido == EstadoPartido.DISPONIBLE
            )
            .all()
        )
