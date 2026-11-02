from sqlalchemy.orm import Session

from app.capa_0_definicion_bd.models.liga_modelos import Liga as LigaModelo, EstadoLiga
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo
from app.capa_0_definicion_bd.models.liga_participantes_modelos import LigaParticipante
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion


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

    def agregar_participante(self, liga: LigaModelo, usuario: UsuarioModelo, id_equipo: int, formacion: Formacion) -> LigaParticipante:
        participacion = LigaParticipante(id_liga=liga.id, id_usuario=usuario.id_usuario, id_equipo=id_equipo, formacion=formacion)
        self.db.add(participacion)
        self.db.commit()
        self.db.refresh(liga)
        self.db.refresh(participacion)
        return participacion
    
    def eliminar_participante(self, liga: LigaModelo, usuario: UsuarioModelo) -> LigaModelo:
        participacion = self.db.query(LigaParticipante).filter_by(id_liga=liga.id, id_usuario=usuario.id_usuario).first()
        if participacion:
            self.db.delete(participacion)
            self.db.commit()
            self.db.refresh(liga)
        return liga
    

    def obtener_ligas_disponibles(self) -> list[LigaModelo]:
        return(self.db.query(LigaModelo)
               .filter(LigaModelo.estado == EstadoLiga.DISPONIBLE)
               .all()
        )
