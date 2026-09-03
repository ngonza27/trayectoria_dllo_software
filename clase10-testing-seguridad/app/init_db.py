from pathlib import Path

from app.dal import models
from app.database import Base, engine


def init_db() -> None:
    Base.metadata.create_all(engine)
    rls_sql = (Path(__file__).parent / "rls.sql").read_text()
    with engine.begin() as conn:
        conn.exec_driver_sql(rls_sql)


if __name__ == "__main__":
    init_db()
    print("Database initialized: tables created, RLS policy and masked view applied.")
