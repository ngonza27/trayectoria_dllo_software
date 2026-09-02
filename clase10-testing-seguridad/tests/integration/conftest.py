"""
Slide 7 — Integration tests: isolate the environment with a real, disposable
database via Testcontainers, exactly as the slide recommends, instead of
mocking the database away. Run this suite with:

    pytest tests/integration

It needs Docker running locally (this spins up a real throwaway Postgres
container per test session — nothing is mocked).

IMPORTANT ordering note: DATABASE_URL must be set, and the container must be
running, *before* anything imports app.config/app.database — that is why
this all happens at module level here (conftest.py is loaded before the
test_*.py files in this directory), and why this suite is run as its own
`pytest tests/integration` invocation rather than mixed into the default
`pytest` run that also collects tests/unit.
"""

import atexit
import os

from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer

# The container's bootstrap user (below) is created by the official Postgres
# image's initdb step, which ALWAYS makes it a superuser — and Postgres never
# applies RLS policies to superusers, full stop, no ALTER can change that.
# So the app must connect as a second, deliberately unprivileged role
# instead, or the RLS tests in test_reservas_crud.py would pass for the
# wrong reason (nobody's reservations were ever actually restricted).
_container = PostgresContainer(
    "postgres:16-alpine", username="postgres_admin", password="postgres_admin", dbname="reservas_db"
)
_container.start()
atexit.register(_container.stop)

_admin_url = _container.get_connection_url()
_admin_engine = create_engine(_admin_url)
with _admin_engine.begin() as conn:
    conn.exec_driver_sql(
        "CREATE ROLE reservas_app WITH LOGIN PASSWORD 'reservas_app' NOSUPERUSER NOBYPASSRLS"
    )
    conn.exec_driver_sql("GRANT ALL ON SCHEMA public TO reservas_app")
_admin_engine.dispose()

os.environ["DATABASE_URL"] = _admin_url.replace(
    "postgres_admin:postgres_admin@", "reservas_app:reservas_app@"
)
# Keep the auth-flow tests below from tripping the login rate limiter
# (slide 17); that behavior gets its own focused test with its own tiny app
# and a deliberately low limit — see test_rate_limit_integration.py.
os.environ.setdefault("RATE_LIMIT_MAX_REQUESTS", "1000")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import engine  # noqa: E402
from app.init_db import init_db  # noqa: E402
from app.main import app  # noqa: E402

init_db()


@pytest.fixture(autouse=True)
def _reset_tables():
    """Slide 6's "independientes entre sí" rule, applied to integration tests too."""
    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE reservas, usuarios, restaurantes RESTART IDENTITY CASCADE")
    yield


@pytest.fixture
def client():
    return TestClient(app)
