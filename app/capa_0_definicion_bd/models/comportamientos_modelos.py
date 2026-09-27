from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from sqlalchemy import ForeignKey, String, Text, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base


class Comportamiento(Base):
    __tablename__ = "comportamientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    nombre = Column(String(100), nullable=False)
    codigo = Column(Text, nullable=False)

    usuario = relationship(
        "Usuario",
        back_populates="comportamientos",
    )