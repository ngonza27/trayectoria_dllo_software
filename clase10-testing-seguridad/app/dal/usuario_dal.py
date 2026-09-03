from sqlalchemy.orm import Session

from app.dal.models import Usuario


def get_by_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def get_by_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.get(Usuario, usuario_id)


def create(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    return usuario
