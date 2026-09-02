from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import schemas
from app.analytics import capture
from app.deps import get_scoped_db, require_role
from app.models import Cuenta

router = APIRouter(prefix="/cuentas", tags=["cuentas"])


def _row_to_cuenta_out(row) -> schemas.CuentaOut:
    return schemas.CuentaOut(
        id=row.id,
        organizacion_id=row.organizacion_id,
        titular=row.titular,
        numero_cuenta=row.numero_cuenta,
        saldo=float(row.saldo),
        created_at=row.created_at,
    )


@router.post("", response_model=schemas.CuentaOut, status_code=status.HTTP_201_CREATED)
def crear_cuenta(
    payload: schemas.CuentaCreate,
    claims: dict = Depends(require_role("usuario", "admin")),
    db: Session = Depends(get_scoped_db),
):
    """
    Slide 7's canonical integration-test example: "POST /orders efectivamente
    inserta el registro ... y responde 201" — here, POST /cuentas.

    Also exercises RLS's WITH CHECK side (slide 22): organizacion_id is taken
    from the caller's *validated JWT claim*, never from the request body, and
    Postgres itself would reject an INSERT for a different organization_id
    than app.org_id even if application code tried to pass one.
    """
    cuenta = Cuenta(
        organizacion_id=int(claims["organizacion_id"]),
        titular=payload.titular,
        numero_cuenta=payload.numero_cuenta,
        saldo=payload.saldo,
    )
    db.add(cuenta)
    db.flush()  # populates cuenta.id/created_at while app.org_id is still set for this transaction
    db.commit()
    capture("crear_cuenta", distinct_id=str(claims["sub"]), properties={"organizacion_id": cuenta.organizacion_id})
    return cuenta


@router.get("", response_model=list[schemas.CuentaOut])
def listar_cuentas(claims: dict = Depends(require_role("usuario", "admin")), db: Session = Depends(get_scoped_db)):
    """
    Slides 20 + 22 together: RLS restricts rows to the caller's organization
    no matter which relation is queried; admins read the base table (full
    account numbers), every other role reads the masked view instead.
    """
    if claims.get("rol") == "admin":
        return db.query(Cuenta).order_by(Cuenta.id).all()

    rows = db.execute(text("SELECT * FROM cuentas_enmascaradas ORDER BY id")).all()
    return [_row_to_cuenta_out(row) for row in rows]


@router.get("/{cuenta_id}", response_model=schemas.CuentaOut)
def obtener_cuenta(
    cuenta_id: int,
    claims: dict = Depends(require_role("usuario", "admin")),
    db: Session = Depends(get_scoped_db),
):
    if claims.get("rol") == "admin":
        cuenta = db.get(Cuenta, cuenta_id)
        if cuenta is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta not found")
        return cuenta

    row = db.execute(text("SELECT * FROM cuentas_enmascaradas WHERE id = :id"), {"id": cuenta_id}).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta not found")
    return _row_to_cuenta_out(row)


@router.put("/{cuenta_id}", response_model=schemas.CuentaOut)
def actualizar_cuenta(
    cuenta_id: int,
    payload: schemas.CuentaUpdate,
    claims: dict = Depends(require_role("admin")),
    db: Session = Depends(get_scoped_db),
):
    """AuthZ beyond RLS (slide 9): only admins may update, even within their own organization's rows."""
    cuenta = db.get(Cuenta, cuenta_id)
    if cuenta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta not found")
    if payload.titular is not None:
        cuenta.titular = payload.titular
    if payload.saldo is not None:
        cuenta.saldo = payload.saldo
    db.commit()
    return cuenta


@router.delete("/{cuenta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cuenta(
    cuenta_id: int,
    claims: dict = Depends(require_role("admin")),
    db: Session = Depends(get_scoped_db),
):
    cuenta = db.get(Cuenta, cuenta_id)
    if cuenta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta not found")
    db.delete(cuenta)
    db.commit()
