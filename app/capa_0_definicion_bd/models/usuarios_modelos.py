from sqlalchemy import Column, Integer, String, Table, ForeignKey
from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    nombre = Column(String, nullable=False)
    id_avatar = Column(Integer, nullable=False)
    contraseña = Column(String, nullable=False)
    nombre_club = Column(String, nullable=False)
