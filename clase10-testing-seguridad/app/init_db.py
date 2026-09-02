"""
Run once to create the schema and apply the RLS policy + masking view:

    python -m app.init_db

Safe to re-run: table creation is skip-if-exists, and app/rls.sql uses
DROP POLICY IF EXISTS / CREATE OR REPLACE VIEW so it is idempotent too.
"""

from pathlib import Path

from app import models  # noqa: F401 — registers the models on Base.metadata
from app.database import Base, engine


def init_db() -> None:
    Base.metadata.create_all(engine)
    rls_sql = (Path(__file__).parent / "rls.sql").read_text()
    with engine.begin() as conn:
        conn.exec_driver_sql(rls_sql)


if __name__ == "__main__":
    init_db()
    print("Database initialized: tables created, RLS policy and masked view applied.")
