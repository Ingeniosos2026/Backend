from enum import Enum

from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from sqlalchemy import CheckConstraint, Enum as SQLEnum
from sqlalchemy import ForeignKey, String, Text, Column, Integer
from sqlalchemy.orm import relationship

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base


class EstadoLiga(str, Enum):
    DISPONIBLE = "Disponible"
    EN_JUEGO = "En juego"
    EN_ESPERA = "En espera"


class Liga(Base):
    __tablename__ = "ligas"

    __table_args__ = (
        CheckConstraint(
            "min_jugadores >= 3",
            name="check_min_jugadores",
        ),
        CheckConstraint(
            "max_jugadores <= 10",
            name="check_max_jugadores",
        ),
        CheckConstraint(
            "min_jugadores <= max_jugadores",
            name="check_jugadores",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    nombre = Column(String(100), nullable=False)
    contraseña = Column(String(100), nullable=True)
    estado = Column(
        SQLEnum(EstadoLiga),
        nullable=False,
        default=EstadoLiga.DISPONIBLE,
    )
    min_jugadores = Column(Integer, nullable=False)
    max_jugadores = Column(Integer, nullable=False)
    duracion_partido = Column(Integer, nullable=False)
    usuario = relationship(
        "Usuario",
        back_populates="ligas",
    )