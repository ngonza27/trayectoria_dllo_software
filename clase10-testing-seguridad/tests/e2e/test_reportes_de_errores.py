import uuid

from playwright.sync_api import Page, expect

from tests.e2e.test_login_flow import _registrar_y_loguear


def test_dashboard_de_un_restaurante_nuevo_dispara_un_error_capturable_por_playwright(page: Page):
    errores_de_pagina = []
    page.on("pageerror", lambda exc: errores_de_pagina.append(exc))

    restaurante = f"fresh-fork-bug2-{uuid.uuid4().hex[:8]}"
    email = f"e2e-bug-{uuid.uuid4().hex[:8]}@puy.com"
    _registrar_y_loguear(page, email, "Segura123!", restaurante=restaurante)
    expect(page.locator("#dashboard")).to_be_visible()

    page.wait_for_timeout(1000)

    assert len(errores_de_pagina) == 1
    assert "JSON" in str(errores_de_pagina[0])
