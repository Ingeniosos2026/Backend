from sqlalchemy.orm import Session

from app.capa_0_definicion_bd.models.liga_modelos import Liga as LigaModelo, EstadoLiga
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo
from app.capa_0_definicion_bd.models.liga_participantes_modelos import LigaParticipante
from app.capa_0_definicion_bd.models.tabla_liga_modelos import TablaLiga
from app.capa_0_definicion_bd.models.fixture_liga_modelos import FixtureLiga
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
    

    def obtener_participantes_liga(self, id_liga: int) -> list[LigaParticipante]:
        return (self.db.query(LigaParticipante).filter(LigaParticipante.id_liga == id_liga).all())
    
    
    def guardar_inicio_liga(self, liga: LigaModelo, tabla: list[TablaLiga], fixture: list[FixtureLiga],) -> None:
        self.db.add_all(tabla)
        self.db.add_all(fixture)
        liga.estado = EstadoLiga.EN_JUEGO
        self.db.commit()


    def obtener_fixture_por_turno(self, id_liga: int, turno: int) -> FixtureLiga:
        return (self.db.query(FixtureLiga).filter(FixtureLiga.id_liga == id_liga, FixtureLiga.turno == turno).first())
    

    def asignar_partido_fixture(self, fixture: FixtureLiga, partido_id: int) -> FixtureLiga:
        fixture.id_partido = partido_id
        return fixture

    def obtener_siguiente_fixture(self, id_liga: int) -> FixtureLiga | None:
        return (self.db.query(FixtureLiga).filter(FixtureLiga.id_liga == id_liga, FixtureLiga.id_partido.is_(None)).order_by(FixtureLiga.turno).first())

    def obtener_participante_por_equipo(self, id_liga: int, id_equipo: int) -> LigaParticipante | None:
        return (self.db.query(LigaParticipante).filter(LigaParticipante.id_liga == id_liga, LigaParticipante.id_equipo == id_equipo).first())
    
    def obtener_registro_tabla(self, id_liga: int, id_equipo: int) -> TablaLiga | None:
        return (self.db.query(TablaLiga).filter(TablaLiga.id_liga == id_liga, TablaLiga.id_equipo == id_equipo).first())

    def finalizar_liga(self, liga: LigaModelo) -> LigaModelo:
        liga.estado = EstadoLiga.FINALIZADA
        self.db.commit()
        self.db.refresh(liga)
        return liga
    
    def actualizar(self) -> None:
        self.db.commit()