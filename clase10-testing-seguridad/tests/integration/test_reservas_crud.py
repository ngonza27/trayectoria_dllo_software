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
    token, _perfil = registrar_y_loguear(client, email="host@puy.com", restaurante="fresh-fork-downtown")

    response = client.post("/reservas", json=_RESERVA_EJEMPLO, headers=_auth_header(token))

    assert response.status_code == 201
    body = response.json()
    assert body["cliente_nombre"] == "Familia Gómez"
    assert body["num_personas"] == 4


def test_non_gerente_sees_the_phone_number_masked(client):
    token, _perfil = registrar_y_loguear(client, email="mesero@puy.com", restaurante="fresh-fork-downtown", rol="mesero")
    client.post("/reservas", json=_RESERVA_EJEMPLO, headers=_auth_header(token))

    response = client.get("/reservas", headers=_auth_header(token))

    assert response.status_code == 200
    [reserva] = response.json()
    assert reserva["telefono"] == "*** *** 4567"


def test_gerente_sees_the_full_phone_number(client):
    token, _perfil = registrar_y_loguear(client, email="gerente@puy.com", restaurante="fresh-fork-downtown", rol="gerente")
    client.post("/reservas", json=_RESERVA_EJEMPLO, headers=_auth_header(token))

    response = client.get("/reservas", headers=_auth_header(token))

    [reserva] = response.json()
    assert reserva["telefono"] == "+573001234567"


def test_rls_blocks_cross_tenant_reads_even_with_no_where_clause_at_all(client):
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

    db = SessionLocal()
    try:
        set_org_context(db, perfil_b["restaurante_id"])
        rows = db.execute(text("SELECT cliente_nombre FROM reservas")).all()
    finally:
        db.close()

    assert [row[0] for row in rows] == ["Cliente B"]


def test_api_also_only_lists_the_callers_own_restaurante(client):
    token_a, _ = registrar_y_loguear(client, email="a2@puy.com", restaurante="fresh-fork-downtown-2")
    token_b, _ = registrar_y_loguear(client, email="b2@puy.com", restaurante="fresh-fork-uptown-2")
    client.post("/reservas", json=_RESERVA_EJEMPLO, headers=_auth_header(token_a))

    response = client.get("/reservas", headers=_auth_header(token_b))

    assert response.json() == [{}]


def test_only_gerente_can_cancel_a_reserva(client):
    gerente_token, _ = registrar_y_loguear(client, email="gerente2@puy.com", restaurante="fresh-fork-riverside", rol="gerente")
    mesero_token, _ = registrar_y_loguear(client, email="mesero2@puy.com", restaurante="fresh-fork-riverside", rol="mesero")
    created = client.post("/reservas", json=_RESERVA_EJEMPLO, headers=_auth_header(gerente_token)).json()

    forbidden_response = client.delete(f"/reservas/{created['id']}", headers=_auth_header(mesero_token))
    allowed_response = client.delete(f"/reservas/{created['id']}", headers=_auth_header(gerente_token))

    assert forbidden_response.status_code == 403
    assert allowed_response.status_code == 204


def test_resumen_of_a_restaurante_with_no_reservas_hits_bug_intencional_2(client):
    token, _perfil = registrar_y_loguear(client, email="sin-reservas@puy.com", restaurante="fresh-fork-vacio")

    with pytest.raises(ZeroDivisionError):
        client.get("/reservas/resumen", headers=_auth_header(token))
