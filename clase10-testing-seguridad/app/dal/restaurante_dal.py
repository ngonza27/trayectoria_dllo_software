from sqlalchemy.orm import Session

from app.dal.models import Restaurante


def get_by_nombre(db: Session, nombre: str) -> Restaurante | None:
    return db.query(Restaurante).filter(Restaurante.nombre == nombre).first()


def create(db: Session, nombre: str) -> Restaurante:
    restaurante = Restaurante(nombre=nombre)
    db.add(restaurante)
    db.flush()
    return restaurante
