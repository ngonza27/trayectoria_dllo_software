from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import schemas
from app.analytics import capture
from app.deps import get_scoped_db, require_role
from app.models import Reserva

router = APIRouter(prefix="/reservas", tags=["reservas"])


def _row_to_reserva_out(row) -> schemas.ReservaOut:
    return schemas.ReservaOut(
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


@router.post("", response_model=schemas.ReservaOut, status_code=status.HTTP_201_CREATED)
def crear_reserva(
    payload: schemas.ReservaCreate,
    claims: dict = Depends(require_role("mesero", "gerente")),
    db: Session = Depends(get_scoped_db),
):
    """
    Slide 7's canonical integration-test example: "POST /orders efectivamente
    inserta el registro ... y responde 201" — here, POST /reservas.

    Also exercises RLS's WITH CHECK side (slide 22): restaurante_id is taken
    from the caller's *validated JWT claim*, never from the request body, and
    Postgres itself would reject an INSERT for a different restaurante_id
    than app.restaurante_id even if application code tried to pass one.
    """
    reserva = Reserva(
        restaurante_id=int(claims["restaurante_id"]),
        cliente_nombre=payload.cliente_nombre,
        telefono=payload.telefono,
        fecha_hora=payload.fecha_hora,
        num_personas=payload.num_personas,
        mesa_numero=payload.mesa_numero,
    )
    db.add(reserva)
    db.flush()  # populates reserva.id/created_at while app.restaurante_id is still set for this transaction
    db.commit()
    capture("crear_reserva", distinct_id=str(claims["sub"]), properties={"restaurante_id": reserva.restaurante_id})
    return reserva


@router.get("", response_model=list[schemas.ReservaOut])
def listar_reservas(claims: dict = Depends(require_role("mesero", "gerente")), db: Session = Depends(get_scoped_db)):
    """
    Slides 20 + 22 together: RLS restricts rows to the caller's restaurant
    no matter which relation is queried; gerentes read the base table (full
    phone numbers), every other role reads the masked view instead.
    """
    if claims.get("rol") == "gerente":
        return db.query(Reserva).order_by(Reserva.id).all()

    rows = db.execute(text("SELECT * FROM reservas_enmascaradas ORDER BY id")).all()
    return [_row_to_reserva_out(row) for row in rows]


@router.get("/resumen", response_model=schemas.ResumenOut)
def resumen_reservas(claims: dict = Depends(require_role("mesero", "gerente")), db: Session = Depends(get_scoped_db)):
    """
    Panel de "hoy" del dashboard: cuántas reservas tiene el restaurante y el
    tamaño de grupo promedio.

    BUG INTENCIONAL #2 (ver GUIA-DE-PRUEBAS.md "Bug intencional #2"): divide
    entre `len(reservas)` sin comprobar que la lista no esté vacía. Un
    restaurante recién registrado no tiene reservas todavía, así que esto
    lanza un ZeroDivisionError sin capturar — Starlette lo convierte en un
    500 real de texto plano (no JSON). static/dashboard.html llama a este
    endpoint sin validar `response.ok`, así que el 500 se propaga como un
    SyntaxError no capturado en el navegador al intentar `response.json()`
    sobre un body que no es JSON — exactamente el tipo de error que
    PostHog's exception autocapture (static/analytics.js) y Playwright's
    "pageerror" (tests/e2e/test_reportes_de_errores.py) están pensados para
    atrapar.
    Definida ANTES de "/{reserva_id}" para que FastAPI no intente parsear
    "resumen" como un id entero.
    """
    reservas = db.query(Reserva).all()
    total_personas = sum(r.num_personas for r in reservas)
    promedio = total_personas / len(reservas)  # ZeroDivisionError cuando reservas == []
    return schemas.ResumenOut(total_reservas=len(reservas), promedio_personas=promedio)


@router.get("/{reserva_id}", response_model=schemas.ReservaOut)
def obtener_reserva(
    reserva_id: int,
    claims: dict = Depends(require_role("mesero", "gerente")),
    db: Session = Depends(get_scoped_db),
):
    if claims.get("rol") == "gerente":
        reserva = db.get(Reserva, reserva_id)
        if reserva is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva not found")
        return reserva

    row = db.execute(text("SELECT * FROM reservas_enmascaradas WHERE id = :id"), {"id": reserva_id}).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva not found")
    return _row_to_reserva_out(row)


@router.put("/{reserva_id}", response_model=schemas.ReservaOut)
def actualizar_reserva(
    reserva_id: int,
    payload: schemas.ReservaUpdate,
    claims: dict = Depends(require_role("gerente")),
    db: Session = Depends(get_scoped_db),
):
    """AuthZ beyond RLS (slide 9): only a gerente may update, even within their own restaurant's rows."""
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva not found")
    if payload.estado is not None:
        reserva.estado = payload.estado
    if payload.mesa_numero is not None:
        reserva.mesa_numero = payload.mesa_numero
    if payload.num_personas is not None:
        reserva.num_personas = payload.num_personas
    db.commit()
    return reserva


@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_reserva(
    reserva_id: int,
    claims: dict = Depends(require_role("gerente")),
    db: Session = Depends(get_scoped_db),
):
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva not found")
    db.delete(reserva)
    db.commit()
