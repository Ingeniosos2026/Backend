from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base


class Equipo(Base):
    __tablename__ = "equipos"

    id_equipo = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)

    usuario = relationship(
        "Usuario",
        back_populates="equipos"
    )

    jugadores = relationship(
        "Jugador",
        back_populates="equipo"
    )

    partido_1 = relationship(
        "Partido",
        foreign_keys="[Partido.id_equipo_1]",
        back_populates="equipo_1"
    )

    partido_2 = relationship(
        "Partido",
        foreign_keys="[Partido.id_equipo_2]",
        back_populates="equipo_2"
    )

