import atexit
import os

from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer

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

os.environ.setdefault("RATE_LIMIT_MAX_REQUESTS", "1000")

import pytest
from fastapi.testclient import TestClient

from app.database import engine
from app.init_db import init_db
from app.main import app

init_db()


@pytest.fixture(autouse=True)
def _reset_tables():
    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE reservas, usuarios, restaurantes RESTART IDENTITY CASCADE")
    yield


@pytest.fixture
def client():
    return TestClient(app)
