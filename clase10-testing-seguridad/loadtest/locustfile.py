import uuid
from datetime import datetime, timedelta, timezone

from locust import HttpUser, between, task


class ReservasUser(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self):
        self.email = f"load-{uuid.uuid4().hex[:10]}@puy.com"
        self.password = "Segura123!"
        with self.client.post(
            "/auth/registro",
            json={"restaurante": "carga-comun", "email": self.email, "password": self.password},
            name="/auth/registro [POST]",
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Bug intencional #1 reproducido: registro devolvió {response.status_code}")
        response = self.client.post("/auth/login", json={"email": self.email, "password": self.password})
        self.token = response.json().get("access_token", "")

    @property
    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def listar_reservas(self):
        self.client.get("/reservas", headers=self._auth_headers, name="/reservas [GET]")

    @task(1)
    def crear_reserva(self):
        fecha_hora = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        self.client.post(
            "/reservas",
            json={
                "cliente_nombre": "Carga de prueba",
                "telefono": str(uuid.uuid4().int)[:10],
                "fecha_hora": fecha_hora,
                "num_personas": 2,
                "mesa_numero": 1,
            },
            headers=self._auth_headers,
            name="/reservas [POST]",
        )

    @task(1)
    def reintentar_login(self):
        self.client.post(
            "/auth/login",
            json={"email": self.email, "password": self.password},
            name="/auth/login [POST]",
        )
