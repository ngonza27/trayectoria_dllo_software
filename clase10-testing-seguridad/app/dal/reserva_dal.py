from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dal.models import Reserva


def create(db: Session, reserva: Reserva) -> Reserva:
    db.add(reserva)
    db.flush()
    return reserva


def list_all(db: Session) -> list[Reserva]:
    return db.query(Reserva).order_by(Reserva.id).all()


def list_masked(db: Session):
    return db.execute(text("SELECT * FROM reservas_enmascaradas ORDER BY id")).all()


def list_for_resumen(db: Session) -> list[Reserva]:
    return db.query(Reserva).all()


def get_by_id(db: Session, reserva_id: int) -> Reserva | None:
    return db.get(Reserva, reserva_id)


def get_masked_by_id(db: Session, reserva_id: int):
    return db.execute(text("SELECT * FROM reservas_enmascaradas WHERE id = :id"), {"id": reserva_id}).first()


def delete(db: Session, reserva: Reserva) -> None:
    db.delete(reserva)
