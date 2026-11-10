from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base


class TablaLiga(Base):
    __tablename__ = "tabla_liga"
    
    id_liga = Column(Integer, ForeignKey("ligas.id", ondelete="CASCADE"), primary_key=True)
    id_equipo = Column(Integer, ForeignKey("equipos.id_equipo"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    partidos_ganados = Column(Integer, default=0, nullable=False)
    partidos_empatados = Column(Integer, default=0, nullable=False)
    partidos_perdidos = Column(Integer, default=0, nullable=False)
    puntos = Column(Integer, default=0, nullable=False)
    goles_a_favor = Column(Integer, default=0, nullable=False)
    goles_en_contra = Column(Integer, default=0, nullable=False)

    equipo = relationship("Equipo")
    usuario = relationship("Usuario")

