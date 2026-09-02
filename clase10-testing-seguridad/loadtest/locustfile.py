"""
Slide 27 — "LOAD TESTS". Locust drives many simulated users against a
*running* server (docker compose up -d && uvicorn app.main:app, same as the
E2E setup) to see how the API behaves under load — and, deliberately, to
watch the rate limiter from slide 17 kick in and return 429s once enough
concurrent users hit /auth/login.

Run it with the web UI:

    locust -f loadtest/locustfile.py --host http://localhost:8000

then open http://localhost:8089, set the number of users/spawn rate, and
watch the request stats. Or headless for a quick smoke run:

    locust -f loadtest/locustfile.py --host http://localhost:8000 \
        --users 20 --spawn-rate 5 --run-time 30s --headless
"""

import uuid

from locust import HttpUser, between, task


class CuentasUser(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self):
        self.email = f"load-{uuid.uuid4().hex[:10]}@puy.com"
        self.password = "Segura123!"
        self.client.post(
            "/auth/registro",
            json={"organizacion": "load-test", "email": self.email, "password": self.password},
        )
        response = self.client.post("/auth/login", json={"email": self.email, "password": self.password})
        self.token = response.json().get("access_token", "")

    @property
    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def listar_cuentas(self):
        self.client.get("/cuentas", headers=self._auth_headers, name="/cuentas [GET]")

    @task(1)
    def crear_cuenta(self):
        self.client.post(
            "/cuentas",
            json={
                "titular": "Carga de prueba",
                "numero_cuenta": str(uuid.uuid4().int)[:16],
                "saldo": 100,
            },
            headers=self._auth_headers,
            name="/cuentas [POST]",
        )

    @task(1)
    def reintentar_login(self):
        # Deliberately hammers the rate-limited endpoint so its 429s show up
        # in the Locust stats — a load test doubling as a rate-limit check.
        self.client.post(
            "/auth/login",
            json={"email": self.email, "password": self.password},
            name="/auth/login [POST]",
        )
