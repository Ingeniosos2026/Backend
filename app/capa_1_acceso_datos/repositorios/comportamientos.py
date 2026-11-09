from typing import List
from sqlalchemy.orm import Session
from app.capa_0_definicion_bd.models.comportamientos_modelos import TipoComportamiento, Comportamiento as ComportamientoModelo
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo

class ComportamientoRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def obtener_comportamiento_por_id_y_usuario(self, comp_id: int, usuario_id: int) -> ComportamientoModelo | None:
        return (
            self.db.query(ComportamientoModelo)
            .filter(ComportamientoModelo.id == comp_id, ComportamientoModelo.id_usuario == usuario_id, ComportamientoModelo.tipo == TipoComportamiento.JUGADOR)
            .first()
        )
    

    def obtener_comportamientos_usuario(self, usuario_id: int) -> List[ComportamientoModelo]:
        return (self.db.query(ComportamientoModelo).filter(ComportamientoModelo.id_usuario == usuario_id, ComportamientoModelo.tipo == TipoComportamiento.JUGADOR).all())

    def crear(self, comportamiento: ComportamientoModelo) -> ComportamientoModelo:
        self.db.add(comportamiento)
        self.db.commit()
        self.db.refresh(comportamiento)
        return comportamiento

    def actualizar(self, comportamiento: ComportamientoModelo) -> ComportamientoModelo:
        self.db.commit()
        self.db.refresh(comportamiento)
        return comportamiento

    def eliminar(self, comportamiento: ComportamientoModelo) -> None:
        self.db.delete(comportamiento)
        self.db.commit()

    def obtener_comportamientos_dt_usuario(self, usuario_id: int) -> List[ComportamientoModelo]:
        return (self.db.query(ComportamientoModelo).filter(ComportamientoModelo.id_usuario == usuario_id, ComportamientoModelo.tipo == TipoComportamiento.DT).all())

    def obtener_comportamiento_dt_actual(self, usuario_id: int) -> ComportamientoModelo:
        return (self.db.query(ComportamientoModelo).join(UsuarioModelo, UsuarioModelo.id_comportamiento_dt == ComportamientoModelo.id)
            .filter(UsuarioModelo.id_usuario == usuario_id, ComportamientoModelo.id_usuario == usuario_id, ComportamientoModelo.tipo == TipoComportamiento.DT).first())

    def obtener_por_id_y_usuario(self, comp_id: int, usuario_id: int) -> ComportamientoModelo | None:
        return (
            self.db.query(ComportamientoModelo).
            filter(ComportamientoModelo.id == comp_id, ComportamientoModelo.id_usuario == usuario_id)
            .first()
        )