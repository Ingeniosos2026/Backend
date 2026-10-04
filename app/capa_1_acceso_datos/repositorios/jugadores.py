from sqlalchemy.orm import Session
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador as JugadorModelo

class JugadorRepositorio:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, jugador: JugadorModelo) -> JugadorModelo:
        self.db.add(jugador)
        self.db.commit()
        self.db.refresh(jugador)
        return jugador

    def obtener_por_id(self, id_jugador: int) -> JugadorModelo | None:
        return (
            self.db.query(JugadorModelo)
            .filter(JugadorModelo.id_jugador == id_jugador)
            .first()
        )

    def contar_jugadores_usuario(self, id_usuario: int) -> int:
        return (
            self.db.query(JugadorModelo)
            .filter(JugadorModelo.id_usuario == id_usuario)
            .count()
        )