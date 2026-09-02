"""
Slide 26 — the class activity: "generar y validar un JWT en el backend, y
cubrir ese flujo con al menos una prueba unitaria y una prueba de
integración." This file is the integration half (tests/unit/test_jwt.py is
the unit half).
"""

from app.config import settings
from tests.integration.helpers import registrar_y_loguear


def test_registro_then_login_then_access_protected_endpoint(client):
    # Arrange
    payload = {"restaurante": "fresh-fork-downtown", "email": "demo@puy.com", "password": "Segura123!", "rol": "mesero"}

    # Act
    register_response = client.post("/auth/registro", json=payload)

    # Assert
    assert register_response.status_code == 201
    assert register_response.json()["email"] == payload["email"]

    # Act
    login_response = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})

    # Assert
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token.count(".") == 2  # header.payload.signature

    # Act
    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    # Assert — the backend validated the JWT and resolved the caller's identity from it
    assert me_response.status_code == 200
    assert me_response.json()["email"] == payload["email"]


def test_duplicate_email_is_rejected(client):
    payload = {"restaurante": "fresh-fork-downtown", "email": "dup@puy.com", "password": "Segura123!"}
    assert client.post("/auth/registro", json=payload).status_code == 201

    response = client.post("/auth/registro", json=payload)

    assert response.status_code == 409


def test_login_with_wrong_password_is_rejected(client):
    client.post("/auth/registro", json={"restaurante": "fresh-fork-downtown", "email": "demo2@puy.com", "password": "Segura123!"})

    response = client.post("/auth/login", json={"email": "demo2@puy.com", "password": "incorrecta"})

    assert response.status_code == 401


def test_protected_endpoint_without_a_token_is_rejected(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_protected_endpoint_with_a_garbage_token_is_rejected(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-jwt"})

    assert response.status_code == 401


def test_client_credentials_grant_issues_a_service_token(client):
    """Slide 18 — Client Credentials: service-to-service, no human user."""
    response = client.post(
        "/auth/token",
        json={"client_id": settings.oauth_client_id, "client_secret": settings.oauth_client_secret},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_client_credentials_grant_rejects_a_wrong_secret(client):
    response = client.post(
        "/auth/token",
        json={"client_id": settings.oauth_client_id, "client_secret": "wrong-secret"},
    )

    assert response.status_code == 401


def test_registrar_y_loguear_helper_returns_restaurante_id(client):
    _token, perfil = registrar_y_loguear(client, email="helper@puy.com", restaurante="helper-restaurant")

    assert perfil["restaurante_id"] is not None


def test_two_users_registering_under_the_same_restaurante_share_its_id(client):
    """
    Sequential (not concurrent) proof that the get-or-create in
    app/routers/auth.py works on the happy path. It does NOT prove the path
    is race-free — it deliberately isn't (Bug intencional #1, see
    GUIA-DE-PRUEBAS.md and loadtest/locustfile.py, which is what actually
    reproduces the race, since it sends real concurrent requests).
    """
    _token1, perfil1 = registrar_y_loguear(client, email="miembro1@puy.com", restaurante="mismo-restaurante")
    _token2, perfil2 = registrar_y_loguear(client, email="miembro2@puy.com", restaurante="mismo-restaurante")

    assert perfil1["restaurante_id"] == perfil2["restaurante_id"]
