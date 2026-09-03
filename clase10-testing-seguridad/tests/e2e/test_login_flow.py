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
    expect(page.locator("#reservas-body")).to_contain_text("*** *** 8877")
