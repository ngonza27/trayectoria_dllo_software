from sqlalchemy.orm import Session

from app.dal import reserva_dal
from app.dal.models import Reserva
from app.services.analytics_service import capture
from app.views.reservas_views import ReservaCreate, ReservaOut, ReservaUpdate, ResumenOut


def _row_to_reserva_out(row) -> ReservaOut:
    return ReservaOut(
        id=row.id,
        restaurante_id=row.restaurante_id,
        cliente_nombre=row.cliente_nombre,
        telefono=row.telefono,
        fecha_hora=row.fecha_hora,
        num_personas=row.num_personas,
        mesa_numero=row.mesa_numero,
        estado=row.estado,
        created_at=row.created_at,
    )


def crear_reserva(db: Session, claims: dict, payload: ReservaCreate) -> Reserva:
    reserva = Reserva(
        restaurante_id=int(claims["restaurante_id"]),
        cliente_nombre=payload.cliente_nombre,
        telefono=payload.telefono,
        fecha_hora=payload.fecha_hora,
        num_personas=payload.num_personas,
        mesa_numero=payload.mesa_numero,
    )
    reserva_dal.create(db, reserva)
    db.commit()
    capture("crear_reserva", distinct_id=str(claims["sub"]), properties={"restaurante_id": reserva.restaurante_id})
    return reserva


def listar_reservas(db: Session, claims: dict) -> list[ReservaOut]:
    if claims.get("rol") == "gerente":
        return reserva_dal.list_all(db)

    rows = reserva_dal.list_masked(db)
    return [_row_to_reserva_out(row) for row in rows]


def resumen_reservas(db: Session) -> ResumenOut:
    reservas = reserva_dal.list_for_resumen(db)
    total_personas = sum(r.num_personas for r in reservas)
    promedio = total_personas / len(reservas)
    return ResumenOut(total_reservas=len(reservas), promedio_personas=promedio)


def obtener_reserva(db: Session, claims: dict, reserva_id: int):
    if claims.get("rol") == "gerente":
        return reserva_dal.get_by_id(db, reserva_id)

    row = reserva_dal.get_masked_by_id(db, reserva_id)
    if row is None:
        return None
    return _row_to_reserva_out(row)


def actualizar_reserva(db: Session, reserva_id: int, payload: ReservaUpdate):
    reserva = reserva_dal.get_by_id(db, reserva_id)
    if reserva is None:
        return None
    if payload.estado is not None:
        reserva.estado = payload.estado
    if payload.mesa_numero is not None:
        reserva.mesa_numero = payload.mesa_numero
    if payload.num_personas is not None:
        reserva.num_personas = payload.num_personas
    db.commit()
    return reserva


def cancelar_reserva(db: Session, reserva_id: int) -> bool:
    reserva = reserva_dal.get_by_id(db, reserva_id)
    if reserva is None:
        return False
    reserva_dal.delete(db, reserva)
    db.commit()
    return True
