from sqlalchemy import Column, Integer, ForeignKey, Enum as SQLenum
from sqlalchemy.orm import relationship
from enum import Enum

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base


class EstadoJugador(str, Enum):
    TITULAR = "titular"
    SUPLENTE = "suplente"

class EquipoJugador(Base):
    __tablename__ = "equipo_jugadores"

    id_equipo = Column(Integer, ForeignKey("equipos.id_equipo", ondelete="CASCADE"), primary_key=True)
    id_jugador = Column(Integer, ForeignKey("jugadores.id_jugador", ondelete="CASCADE"), primary_key=True)
    estado = Column(SQLenum(EstadoJugador), nullable=False, default=EstadoJugador.SUPLENTE)

    equipo = relationship(
        "Equipo",
        back_populates="jugadores")

    jugador = relationship(
        "Jugador",
        back_populates="equipos")