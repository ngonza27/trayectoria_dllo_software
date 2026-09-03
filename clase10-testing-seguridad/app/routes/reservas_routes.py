from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers import reservas_controller
from app.deps import get_scoped_db, require_role
from app.views.reservas_views import ReservaCreate, ReservaOut, ReservaUpdate, ResumenOut

router = APIRouter(prefix="/reservas", tags=["reservas"])


@router.post("", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
def crear_reserva(
    payload: ReservaCreate,
    claims: dict = Depends(require_role("mesero", "gerente")),
    db: Session = Depends(get_scoped_db),
):
    return reservas_controller.crear_reserva(payload, claims, db)


@router.get("", response_model=list[ReservaOut])
def listar_reservas(claims: dict = Depends(require_role("mesero", "gerente")), db: Session = Depends(get_scoped_db)):
    return reservas_controller.listar_reservas(claims, db)


@router.get("/resumen", response_model=ResumenOut)
def resumen_reservas(claims: dict = Depends(require_role("mesero", "gerente")), db: Session = Depends(get_scoped_db)):
    return reservas_controller.resumen_reservas(claims, db)


@router.get("/{reserva_id}", response_model=ReservaOut)
def obtener_reserva(
    reserva_id: int,
    claims: dict = Depends(require_role("mesero", "gerente")),
    db: Session = Depends(get_scoped_db),
):
    return reservas_controller.obtener_reserva(reserva_id, claims, db)


@router.put("/{reserva_id}", response_model=ReservaOut)
def actualizar_reserva(
    reserva_id: int,
    payload: ReservaUpdate,
    claims: dict = Depends(require_role("gerente")),
    db: Session = Depends(get_scoped_db),
):
    return reservas_controller.actualizar_reserva(reserva_id, payload, claims, db)


@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_reserva(
    reserva_id: int,
    claims: dict = Depends(require_role("gerente")),
    db: Session = Depends(get_scoped_db),
):
    reservas_controller.cancelar_reserva(reserva_id, claims, db)
