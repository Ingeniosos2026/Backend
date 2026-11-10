from sqlalchemy import Column, Integer, ForeignKey, Enum as SQLenum
from app.capa_0_definicion_bd.models.partidos_modelos import Formacion
from sqlalchemy.orm import relationship
from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base


class LigaParticipante(Base):
    __tablename__ = "liga_participantes"
    
    id_liga = Column(Integer, ForeignKey("ligas.id", ondelete="CASCADE"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)
    id_equipo = Column(Integer, ForeignKey("equipos.id_equipo"), nullable=False)
    formacion = Column(SQLenum(Formacion), nullable=False)

    liga = relationship(
        "Liga", 
        back_populates="participantes")
    
    usuario = relationship(
        "Usuario", 
        back_populates="ligas_unidas")
    
    equipo = relationship("Equipo")

