"""
Slide 7's canonical example ("POST /orders inserta el registro ... responde
201"), slide 22 (Row-Level Security), and slide 23 (column masking) — all
against a real, disposable Postgres via Testcontainers (see conftest.py).
"""

from sqlalchemy import text

from app.database import SessionLocal, set_org_context
from tests.integration.helpers import registrar_y_loguear


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_post_cuentas_inserts_a_row_and_responds_201(client):
    # Arrange
    token, _perfil = registrar_y_loguear(client, email="host@puy.com", organizacion="fresh-fork")

    # Act
    response = client.post(
        "/cuentas",
        json={"titular": "Fresh Fork SAS", "numero_cuenta": "1111222233334444", "saldo": 500},
        headers=_auth_header(token),
    )

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["titular"] == "Fresh Fork SAS"
    assert body["saldo"] == 500


def test_non_admin_sees_the_account_number_masked(client):
    # Arrange
    token, _perfil = registrar_y_loguear(client, email="usuario@puy.com", organizacion="fresh-fork", rol="usuario")
    client.post(
        "/cuentas",
        json={"titular": "Fresh Fork SAS", "numero_cuenta": "1111222233334444", "saldo": 500},
        headers=_auth_header(token),
    )

    # Act
    response = client.get("/cuentas", headers=_auth_header(token))

    # Assert
    assert response.status_code == 200
    [cuenta] = response.json()
    assert cuenta["numero_cuenta"] == "**** **** **** 4444"


def test_admin_sees_the_full_account_number(client):
    # Arrange
    token, _perfil = registrar_y_loguear(client, email="admin@puy.com", organizacion="fresh-fork", rol="admin")
    client.post(
        "/cuentas",
        json={"titular": "Fresh Fork SAS", "numero_cuenta": "1111222233334444", "saldo": 500},
        headers=_auth_header(token),
    )

    # Act
    response = client.get("/cuentas", headers=_auth_header(token))

    # Assert
    [cuenta] = response.json()
    assert cuenta["numero_cuenta"] == "1111222233334444"


def test_rls_blocks_cross_tenant_reads_even_with_no_where_clause_at_all(client):
    """
    The strongest possible proof of slide 22's promise: query the base table
    with ZERO filtering in the SQL itself, as org B — RLS must still hide
    org A's row, because the database enforces it, not the application code.
    """
    # Arrange
    token_a, _ = registrar_y_loguear(client, email="a@puy.com", organizacion="org-a")
    token_b, perfil_b = registrar_y_loguear(client, email="b@puy.com", organizacion="org-b")

    client.post(
        "/cuentas",
        json={"titular": "Cliente A", "numero_cuenta": "1111111111111111", "saldo": 100},
        headers=_auth_header(token_a),
    )
    client.post(
        "/cuentas",
        json={"titular": "Cliente B", "numero_cuenta": "2222222222222222", "saldo": 200},
        headers=_auth_header(token_b),
    )

    # Act
    db = SessionLocal()
    try:
        set_org_context(db, perfil_b["organizacion_id"])
        rows = db.execute(text("SELECT titular FROM cuentas")).all()  # no WHERE clause
    finally:
        db.close()

    # Assert
    assert [row[0] for row in rows] == ["Cliente B"]


def test_api_also_only_lists_the_callers_own_organization(client):
    # Arrange
    token_a, _ = registrar_y_loguear(client, email="a2@puy.com", organizacion="org-a2")
    token_b, _ = registrar_y_loguear(client, email="b2@puy.com", organizacion="org-b2")
    client.post(
        "/cuentas",
        json={"titular": "Cliente A2", "numero_cuenta": "3333333333333333", "saldo": 10},
        headers=_auth_header(token_a),
    )

    # Act
    response = client.get("/cuentas", headers=_auth_header(token_b))

    # Assert
    assert response.json() == []


def test_only_admin_can_delete_a_cuenta(client):
    # Arrange
    admin_token, _ = registrar_y_loguear(client, email="admin2@puy.com", organizacion="fresh-fork2", rol="admin")
    usuario_token, _ = registrar_y_loguear(client, email="usuario2@puy.com", organizacion="fresh-fork2", rol="usuario")
    created = client.post(
        "/cuentas",
        json={"titular": "Fresh Fork SAS", "numero_cuenta": "4444444444444444", "saldo": 0},
        headers=_auth_header(admin_token),
    ).json()

    # Act
    forbidden_response = client.delete(f"/cuentas/{created['id']}", headers=_auth_header(usuario_token))
    allowed_response = client.delete(f"/cuentas/{created['id']}", headers=_auth_header(admin_token))

    # Assert
    assert forbidden_response.status_code == 403
    assert allowed_response.status_code == 204
