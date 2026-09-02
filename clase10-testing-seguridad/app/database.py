from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
# expire_on_commit=False: without it, SQLAlchemy re-SELECTs every attribute
# the first time it's touched after a commit — which, on the RLS-protected
# `reservas` table, would run in a *new* transaction where app.restaurante_id
# hasn't been set yet (SET LOCAL only lasts for the transaction it ran in),
# and come back empty. Routes rely on the in-memory object they already built
# instead, and use db.flush() (same transaction, no commit) when they need
# a server-populated value like the generated id.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def set_org_context(db: Session, restaurante_id: int) -> None:
    """
    Slide 22 — Row-Level Security: the RLS policy on `reservas` checks
    current_setting('app.restaurante_id'). We set it as the very first
    statement of the request's DB transaction (SET LOCAL, so it never leaks
    to other requests sharing a pooled connection), from the *validated JWT
    claim*, never from a client-supplied parameter.
    """
    db.execute(text("SET LOCAL app.restaurante_id = :restaurante_id"), {"restaurante_id": str(restaurante_id)})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
