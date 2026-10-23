from sqlalchemy import Column, Integer, ForeignKey
from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base

class LigaParticipante(Base):
    __tablename__ = "liga_participantes"
    
    id_liga = Column(Integer, ForeignKey("ligas.id", ondelete="CASCADE"), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)