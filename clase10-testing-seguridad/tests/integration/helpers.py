from fastapi.testclient import TestClient


def registrar_y_loguear(
    client: TestClient,
    *,
    email: str,
    restaurante: str,
    rol: str = "mesero",
    password: str = "Segura123!",
) -> tuple[str, dict]:
    client.post(
        "/auth/registro",
        json={"restaurante": restaurante, "email": email, "password": password, "rol": rol},
    )
    login_response = client.post("/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    return token, me_response.json()
