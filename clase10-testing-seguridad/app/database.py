from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def set_org_context(db: Session, restaurante_id: int) -> None:
    db.execute(text("SET LOCAL app.restaurante_id = :restaurante_id"), {"restaurante_id": str(restaurante_id)})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
