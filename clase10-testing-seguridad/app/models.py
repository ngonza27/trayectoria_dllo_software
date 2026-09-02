from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Restaurante(Base):
    """One of the 3 locations of the "Fresh Fork" group used as this demo's tenants."""

    __tablename__ = "restaurantes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True)


class Usuario(Base):
    """Slide 9/12/13 — AuthN principal. `rol` drives AuthZ decisions."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(20), default="mesero")  # "mesero" | "gerente"
    restaurante_id: Mapped[int] = mapped_column(ForeignKey("restaurantes.id"))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    restaurante: Mapped["Restaurante"] = relationship()


class Reserva(Base):
    """
    Slide 22/23 — the exact table the RLS policy and masking view in
    app/rls.sql target: `restaurante_id` is the RLS partition key, `telefono`
    is the column the masked view hides.
    """

    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(primary_key=True)
    restaurante_id: Mapped[int] = mapped_column(ForeignKey("restaurantes.id"))
    cliente_nombre: Mapped[str] = mapped_column(String(120))
    telefono: Mapped[str] = mapped_column(String(20))
    fecha_hora: Mapped[datetime]
    num_personas: Mapped[int] = mapped_column(Integer)
    mesa_numero: Mapped[int] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")  # pendiente|confirmada|cancelada
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
