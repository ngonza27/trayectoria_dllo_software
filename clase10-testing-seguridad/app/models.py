from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Organizacion(Base):
    __tablename__ = "organizaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True)


class Usuario(Base):
    """Slide 9/12/13 — AuthN principal. `rol` drives AuthZ decisions."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(20), default="usuario")  # "usuario" | "admin"
    organizacion_id: Mapped[int] = mapped_column(ForeignKey("organizaciones.id"))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    organizacion: Mapped["Organizacion"] = relationship()


class Cuenta(Base):
    """
    Slide 22/23 — the exact `cuentas` table the RLS policy and masking view
    in app/rls.sql target: `organizacion_id` is the RLS partition key,
    `numero_cuenta` is the column the masked view hides.
    """

    __tablename__ = "cuentas"

    id: Mapped[int] = mapped_column(primary_key=True)
    organizacion_id: Mapped[int] = mapped_column(ForeignKey("organizaciones.id"))
    titular: Mapped[str] = mapped_column(String(120))
    numero_cuenta: Mapped[str] = mapped_column(String(20))
    saldo: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
