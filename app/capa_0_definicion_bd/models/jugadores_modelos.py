from sqlalchemy import Column, Integer, String, Table, ForeignKey, Enum as SQLenum
from sqlalchemy.orm import relationship
from enum import Enum
from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base



class EstadoJugador(str, Enum):
    TITULAR = "titular"
    SUPLENTE = "suplente"
    NINGUNO = "ninguno"

class Jugador(Base):
    __tablename__ = "jugadores"


    id_jugador = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    id_comportamiento = Column(Integer, ForeignKey("comportamientos.id", ondelete="RESTRICT"), nullable=True)
    id_equipo = Column(Integer, ForeignKey("equipos.id_equipo", ondelete="SET NULL"), nullable=True)
    nombre_jugador = Column(String(50), nullable=False)
    control = Column(Integer, nullable=False)
    agilidad = Column(Integer, nullable=False)
    fuerza = Column(Integer, nullable=False)
    poder = Column(Integer, nullable=False)
    velocidad = Column(Integer, nullable=False)
    estado = Column(SQLenum(EstadoJugador), nullable=False, default=EstadoJugador.NINGUNO)


    usuario = relationship(
        "Usuario", 
        back_populates="jugadores"
    )
    
    comportamiento = relationship(
        "Comportamiento", 
         back_populates="jugadores"
    )

    equipo = relationship(
        "Equipo",
        back_populates="jugadores"
    )

    equipos_amistosos = relationship(
        "Equipo",
        secondary="equipo_jugadores",
        back_populates="jugadores_amistosos"
    )