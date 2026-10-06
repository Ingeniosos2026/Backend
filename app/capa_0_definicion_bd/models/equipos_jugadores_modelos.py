from sqlalchemy import Column, Integer, ForeignKey
from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base

class EquipoJugador(Base):
    __tablename__ = "equipo_jugadores"

    id_equipo = Column(Integer, ForeignKey("equipos.id_equipo", ondelete="CASCADE"), primary_key=True)
    id_jugador = Column(Integer, ForeignKey("jugadores.id_jugador", ondelete="CASCADE"), primary_key=True)