from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base

class Jugador(Base):
    __tablename__ = "jugadores"


    id_jugador = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    id_comportamiento = Column(Integer, ForeignKey("comportamientos.id", ondelete="RESTRICT"), nullable=True)
    nombre_jugador = Column(String(50), nullable=False)
    control = Column(Integer, nullable=False)
    agilidad = Column(Integer, nullable=False)
    fuerza = Column(Integer, nullable=False)
    poder = Column(Integer, nullable=False)
    velocidad = Column(Integer, nullable=False)

    usuario = relationship(
        "Usuario", 
        back_populates="jugadores"
    )
    
    comportamiento = relationship(
        "Comportamiento", 
         back_populates="jugadores"
    )