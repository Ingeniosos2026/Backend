from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base


class Comportamiento(Base):
    __tablename__ = "comportamientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    codigo: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    usuario: Mapped["Usuario"] = relationship(
        back_populates="comportamientos"
    )