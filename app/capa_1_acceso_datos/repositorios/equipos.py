from sqlalchemy.orm import Session
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo as EquipoModelo
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador as JugadorModelo
from app.capa_0_definicion_bd.models.equipos_jugadores_modelos import EquipoJugador, EstadoJugador

class EquipoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, equipo: EquipoModelo) -> EquipoModelo:
        self.db.add(equipo)
        self.db.commit()
        self.db.refresh(equipo)
        return equipo

    def obtener_por_id(self, id_equipo: int) -> EquipoModelo | None:
        return (
            self.db.query(EquipoModelo)
            .filter(EquipoModelo.id_equipo == id_equipo)
            .first()
        )

    def agregar_jugador(self, equipo: EquipoModelo, jugador: JugadorModelo, estado: EstadoJugador) -> EquipoModelo:
        j = EquipoJugador(id_equipo=equipo.id_equipo, id_jugador=jugador.id_jugador, estado=estado)
        self.db.add(j)
        self.db.commit()
        self.db.refresh(j)
        return j