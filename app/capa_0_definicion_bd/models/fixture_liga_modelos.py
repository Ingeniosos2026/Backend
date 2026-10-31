from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base


class FixtureLiga(Base):
    __tablename__ = "fixture_liga"

    id_fixture = Column(Integer, primary_key=True, autoincrement=True)
    id_liga = Column(Integer, ForeignKey("ligas.id", ondelete="CASCADE"), nullable=False)
    id_equipo_izq = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=False)
    id_equipo_der = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=False)
    id_partido = Column(Integer, ForeignKey("partidos.id_partido"), nullable=True, unique=True)
    turno = Column(Integer, nullable=False)

    equipo_izq = relationship("Equipo", foreign_keys=[id_equipo_izq])
    equipo_der = relationship("Equipo", foreign_keys=[id_equipo_der])