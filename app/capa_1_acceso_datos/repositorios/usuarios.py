from sqlalchemy.orm import Session
from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario as UsuarioModelo


class UsuarioRepositorio:
    def __init__(self, db: Session):
        self.db = db
    
    def crear(self, usuario: UsuarioModelo) -> UsuarioModelo:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
    
    def obtener_por_email(self, email: str) -> UsuarioModelo | None:
        return (
            self.db.query(UsuarioModelo)
            .filter(UsuarioModelo.email == email)
            .first()
        )

    def obtener_por_id(self, id_usuario: int) -> UsuarioModelo | None:
        return (
            self.db.query(UsuarioModelo)
            .filter(UsuarioModelo.id_usuario == id_usuario)
            .first()
        )