"""
Slide 27 — "LOAD TESTS". Locust drives many simulated users against a
*running* server (docker compose up -d && uvicorn app.main:app, same as the
E2E setup) to see how the API behaves under load — and, deliberately, to
reproduce Bug intencional #1 (see GUIA-DE-PRUEBAS.md and
app/routers/auth.py): every simulated user registers under the SAME
restaurant name, so once enough of them spawn "at the same time", the
get-or-create race in POST /auth/registro produces real 500s, visible as red
failures in Locust's own report. You should also see 429 Too Many Requests
in the /auth/login stats once enough concurrent users hit the rate limiter
from slide 17.

Run it with the web UI:

    locust -f loadtest/locustfile.py --host http://localhost:8000

then open http://localhost:8089, set the number of users/spawn rate, and
watch the request stats — Charts and Failures. Or headless for a quick
smoke run that prints a summary table at the end:

    locust -f loadtest/locustfile.py --host http://localhost:8000 \
        --users 30 --spawn-rate 30 --run-time 20s --headless
"""

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
            # Same restaurant name for every simulated user, on purpose —
            # this is what creates contention on the get-or-create in
            # app/routers/auth.py (Bug intencional #1).
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
        # Deliberately hammers the rate-limited endpoint so its 429s show up
        # in the Locust stats — a load test doubling as a rate-limit check.
        self.client.post(
            "/auth/login",
            json={"email": self.email, "password": self.password},
            name="/auth/login [POST]",
        )
