from sqlalchemy import CheckConstraint, Column, Integer, String, Table, ForeignKey, Enum as SQLenum
from sqlalchemy.orm import relationship, synonym
from enum import Enum, IntEnum
from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base

class Formacion(IntEnum):
    FORMACION_1 = 1
    FORMACION_2 = 2
    FORMACION_3 = 3
    FORMACION_4 = 4

class TipoPartido(str, Enum):
    AMISTOSO = "amistoso"
    LIGA = "liga"

class EstadoPartido(str, Enum):
    DISPONIBLE = "disponible"
    PENDIENTE = "pendiente"
    EN_CURSO = "en_curso"
    TERMINADO = "terminado"

class Partido(Base):
    __tablename__ = "partidos"
    __table_args__ = (
        CheckConstraint("formacion BETWEEN 1 AND 4", name="check_partido_formacion"),
    )

    id_partido = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario_1 = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    id_usuario_2 = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=True)
    id_equipo_1 = Column(Integer, ForeignKey("equipos.id_equipo", ondelete="CASCADE"), nullable=False)
    id_equipo_2 = Column(Integer, ForeignKey("equipos.id_equipo", ondelete="CASCADE"), nullable=True)
    duracion_partido = Column(Integer, nullable=False)
    formacion = Column(Integer, nullable=False)
    tipo_partido = Column(SQLenum(TipoPartido), nullable=False)
    estado_partido = Column(SQLenum(EstadoPartido), nullable=False, default=EstadoPartido.DISPONIBLE)

    duracion = synonym("duracion_partido")
    tipo = synonym("tipo_partido")
    estado = synonym("estado_partido")

    usuario_1 = relationship(
        "Usuario",
        foreign_keys=[id_usuario_1],
        back_populates="partido_1"
    )

    usuario_2 = relationship(
        "Usuario",
        foreign_keys=[id_usuario_2],
        back_populates="partido_2"
    )

    equipo_1 = relationship(
        "Equipo",
        foreign_keys=[id_equipo_1],
        back_populates="partido_1"
    )

    equipo_2 = relationship(
        "Equipo",
        foreign_keys=[id_equipo_2],
        back_populates="partido_2"
    )