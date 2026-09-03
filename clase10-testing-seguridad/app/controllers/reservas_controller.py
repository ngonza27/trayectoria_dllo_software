from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services import reservas_service
from app.views.reservas_views import ReservaCreate, ReservaOut, ReservaUpdate, ResumenOut


def crear_reserva(payload: ReservaCreate, claims: dict, db: Session) -> ReservaOut:
    return reservas_service.crear_reserva(db, claims, payload)


def listar_reservas(claims: dict, db: Session) -> list[ReservaOut]:
    return reservas_service.listar_reservas(db, claims)


def resumen_reservas(claims: dict, db: Session) -> ResumenOut:
    return reservas_service.resumen_reservas(db)


def obtener_reserva(reserva_id: int, claims: dict, db: Session) -> ReservaOut:
    reserva = reservas_service.obtener_reserva(db, claims, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva not found")
    return reserva


def actualizar_reserva(reserva_id: int, payload: ReservaUpdate, claims: dict, db: Session) -> ReservaOut:
    reserva = reservas_service.actualizar_reserva(db, reserva_id, payload)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva not found")
    return reserva


def cancelar_reserva(reserva_id: int, claims: dict, db: Session) -> None:
    deleted = reservas_service.cancelar_reserva(db, reserva_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva not found")
