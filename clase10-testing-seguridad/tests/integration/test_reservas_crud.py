"""
Slide 7's canonical example ("POST /orders inserta el registro ... responde
201"), slide 22 (Row-Level Security), and slide 23 (column masking) — all
against a real, disposable Postgres via Testcontainers (see conftest.py).
"""

import pytest
from sqlalchemy import text

from app.database import SessionLocal, set_org_context
from tests.integration.helpers import registrar_y_loguear


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


_RESERVA_EJEMPLO = {
    "cliente_nombre": "Familia Gómez",
    "telefono": "+573001234567",
    "fecha_hora": "2026-09-10T20:00:00+00:00",
    "num_personas": 4,
    "mesa_numero": 7,
}


def test_post_reservas_inserts_a_row_and_responds_201(client):
    # Arrange
    token, _perfil = registrar_y_loguear(client, email="host@puy.com", restaurante="fresh-fork-downtown")

    # Act
    response = client.post("/reservas", json=_RESERVA_EJEMPLO, headers=_auth_header(token))

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["cliente_nombre"] == "Familia Gómez"
    assert body["num_personas"] == 4


def test_non_gerente_sees_the_phone_number_masked(client):
    # Arrange
    token, _perfil = registrar_y_loguear(client, email="mesero@puy.com", restaurante="fresh-fork-downtown", rol="mesero")
    client.post("/reservas", json=_RESERVA_EJEMPLO, headers=_auth_header(token))

    # Act
    response = client.get("/reservas", headers=_auth_header(token))

    # Assert
    assert response.status_code == 200
    [reserva] = response.json()
    assert reserva["telefono"] == "*** *** 4567"


def test_gerente_sees_the_full_phone_number(client):
    # Arrange
    token, _perfil = registrar_y_loguear(client, email="gerente@puy.com", restaurante="fresh-fork-downtown", rol="gerente")
    client.post("/reservas", json=_RESERVA_EJEMPLO, headers=_auth_header(token))

    # Act
    response = client.get("/reservas", headers=_auth_header(token))

    # Assert
    [reserva] = response.json()
    assert reserva["telefono"] == "+573001234567"


def test_rls_blocks_cross_tenant_reads_even_with_no_where_clause_at_all(client):
    """
    The strongest possible proof of slide 22's promise: query the base table
    with ZERO filtering in the SQL itself, as restaurant B — RLS must still
    hide restaurant A's row, because the database enforces it, not the
    application code.
    """
    # Arrange
    token_a, _ = registrar_y_loguear(client, email="a@puy.com", restaurante="fresh-fork-downtown")
    token_b, perfil_b = registrar_y_loguear(client, email="b@puy.com", restaurante="fresh-fork-uptown")

    client.post(
        "/reservas",
        json={**_RESERVA_EJEMPLO, "cliente_nombre": "Cliente A"},
        headers=_auth_header(token_a),
    )
    client.post(
        "/reservas",
        json={**_RESERVA_EJEMPLO, "cliente_nombre": "Cliente B"},
        headers=_auth_header(token_b),
    )

    # Act
    db = SessionLocal()
    try:
        set_org_context(db, perfil_b["restaurante_id"])
        rows = db.execute(text("SELECT cliente_nombre FROM reservas")).all()  # no WHERE clause
    finally:
        db.close()

    # Assert
    assert [row[0] for row in rows] == ["Cliente B"]


def test_api_also_only_lists_the_callers_own_restaurante(client):
    # Arrange
    token_a, _ = registrar_y_loguear(client, email="a2@puy.com", restaurante="fresh-fork-downtown-2")
    token_b, _ = registrar_y_loguear(client, email="b2@puy.com", restaurante="fresh-fork-uptown-2")
    client.post("/reservas", json=_RESERVA_EJEMPLO, headers=_auth_header(token_a))

    # Act
    response = client.get("/reservas", headers=_auth_header(token_b))

    # Assert
    assert response.json() == []


def test_only_gerente_can_cancel_a_reserva(client):
    # Arrange
    gerente_token, _ = registrar_y_loguear(client, email="gerente2@puy.com", restaurante="fresh-fork-riverside", rol="gerente")
    mesero_token, _ = registrar_y_loguear(client, email="mesero2@puy.com", restaurante="fresh-fork-riverside", rol="mesero")
    created = client.post("/reservas", json=_RESERVA_EJEMPLO, headers=_auth_header(gerente_token)).json()

    # Act
    forbidden_response = client.delete(f"/reservas/{created['id']}", headers=_auth_header(mesero_token))
    allowed_response = client.delete(f"/reservas/{created['id']}", headers=_auth_header(gerente_token))

    # Assert
    assert forbidden_response.status_code == 403
    assert allowed_response.status_code == 204


def test_resumen_of_a_restaurante_with_no_reservas_hits_bug_intencional_2(client):
    """
    Bug intencional #2 (ver GUIA-DE-PRUEBAS.md "Bug intencional #2" y
    docs/security-architecture.md). GET /reservas/resumen calcula un
    promedio dividiendo entre `len(reservas)` sin comprobar que la lista no
    esté vacía. Un restaurante recién registrado no tiene reservas todavía,
    así que el endpoint revienta con un ZeroDivisionError real y sin
    capturar en vez de responder, por ejemplo, con un promedio de 0.

    FastAPI's TestClient re-raises unhandled server exceptions by default
    (raise_server_exceptions=True) instead of turning them into an HTTP 500
    response — which is exactly what makes this test such a clear, literal
    demonstration of "un error que se puede ver en el reporte de la
    librería": remove the `pytest.raises` below and pytest's own failure
    report will print the full ZeroDivisionError traceback.
    """
    token, _perfil = registrar_y_loguear(client, email="sin-reservas@puy.com", restaurante="fresh-fork-vacio")

    with pytest.raises(ZeroDivisionError):
        client.get("/reservas/resumen", headers=_auth_header(token))
