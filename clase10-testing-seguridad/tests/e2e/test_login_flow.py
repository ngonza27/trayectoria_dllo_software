"""
Slide 9/10 — End-to-End with Playwright. This is the Python equivalent
(pytest-playwright) of the exact JS/TS example on slide 10: navigate, fill
#email/#password, click the submit button, assert a post-login element is
visible. We use the Python API for consistency with the rest of this
FastAPI/pytest stack; the underlying engine and semantics are identical.

Requires a REAL running server and Postgres (this is the slowest, most
expensive layer of the pyramid — slide 5) — see docs/security-architecture.md
"Cómo correr cada capa de la pirámide" for the exact commands:

    docker compose up -d
    python -m app.init_db
    uvicorn app.main:app --reload
    playwright install chromium   # once
    pytest tests/e2e --base-url=http://localhost:8000
"""

import uuid

from playwright.sync_api import Page, expect


def _registrar_y_loguear(page: Page, email: str, password: str, restaurante: str = "fresh-fork-e2e") -> None:
    page.goto("/registro.html")
    page.fill("#restaurante", restaurante)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click('button[type="submit"]')
    page.wait_for_url("**/login.html")

    page.fill("#email", email)
    page.fill("#password", password)
    page.click('button[type="submit"]')


def test_un_usuario_puede_registrarse_e_iniciar_sesion(page: Page):
    email = f"e2e-{uuid.uuid4().hex[:8]}@puy.com"
    password = "Segura123!"

    _registrar_y_loguear(page, email, password)

    expect(page.locator("#dashboard")).to_be_visible()
    expect(page.locator("#whoami")).to_contain_text(email)


def test_login_con_credenciales_invalidas_muestra_un_error(page: Page):
    page.goto("/login.html")

    page.fill("#email", "no-existe@puy.com")
    page.fill("#password", "loquesea")
    page.click('button[type="submit"]')

    expect(page.locator("#error")).to_be_visible()
    expect(page.locator("#error")).to_contain_text("inválidas")


def test_un_usuario_puede_crear_una_reserva_desde_el_dashboard(page: Page):
    email = f"e2e-{uuid.uuid4().hex[:8]}@puy.com"
    password = "Segura123!"
    _registrar_y_loguear(page, email, password)
    expect(page.locator("#dashboard")).to_be_visible()

    page.fill("#cliente_nombre", "Cliente E2E")
    page.fill("#telefono", "+573009998877")
    page.fill("#fecha_hora", "2026-09-10T20:00")
    page.fill("#num_personas", "3")
    page.fill("#mesa_numero", "5")
    page.click('#crear-form button[type="submit"]')

    expect(page.locator("#reservas-body")).to_contain_text("Cliente E2E")
    # This user registered without an explicit role, so the API defaults to
    # "mesero" and the phone number comes back masked — slide 20/23.
    expect(page.locator("#reservas-body")).to_contain_text("*** *** 8877")
