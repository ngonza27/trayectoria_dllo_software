"""
"Induce un error atrapable por Playwright" — Bug intencional #2. Ver
GUIA-DE-PRUEBAS.md "Bug intencional #2" y app/routers/reservas.py
(`resumen_reservas`) / static/dashboard.html (`cargarResumen`) para el resto
de la cadena: un restaurante recién registrado no tiene reservas todavía,
GET /reservas/resumen divide entre cero en el backend (500 sin capturar), y
el frontend -- que no valida `response.ok` antes de leer el body -- lanza un
SyntaxError no capturado: el 500 real de Starlette (`ServerErrorMiddleware`,
sin DEBUG) responde texto plano ("Internal Server Error"), no JSON, así que
`await response.json()` revienta al intentar parsearlo.

Playwright expone este tipo de error de fábrica: basta con escuchar el
evento "pageerror" de la página, sin instrumentar nada más en el código de
la app. Esto es, además, exactamente lo que PostHog's exception autocapture
(static/analytics.js, `capture_exceptions: true`) captura del lado del
navegador — si tienes POSTHOG_PROJECT_API_KEY configurado en .env, correr
este mismo test con un navegador visible (--headed) genera una sesión real
que puedes buscar en PostHog (Activity → Error tracking, y su replay en
Session replay) con el mismo error.
"""

import uuid

from playwright.sync_api import Page, expect

from tests.e2e.test_login_flow import _registrar_y_loguear


def test_dashboard_de_un_restaurante_nuevo_dispara_un_error_capturable_por_playwright(page: Page):
    errores_de_pagina = []
    page.on("pageerror", lambda exc: errores_de_pagina.append(exc))

    # Un restaurante único y nunca antes visto: si reutilizáramos
    # "fresh-fork-e2e" (el que usan los demás tests E2E), ya tendría
    # reservas de una corrida anterior y el ZeroDivisionError no ocurriría
    # — el bug depende de que la lista de reservas esté realmente vacía.
    restaurante = f"fresh-fork-bug2-{uuid.uuid4().hex[:8]}"
    email = f"e2e-bug-{uuid.uuid4().hex[:8]}@puy.com"
    _registrar_y_loguear(page, email, "Segura123!", restaurante=restaurante)
    expect(page.locator("#dashboard")).to_be_visible()

    # cargarResumen() se dispara sin `await` (fire-and-forget) en
    # dashboard.html, así que el rechazo asíncrono llega un instante después
    # de que el dashboard ya es visible — hay que darle tiempo al fetch.
    page.wait_for_timeout(1000)

    assert len(errores_de_pagina) == 1
    assert "JSON" in str(errores_de_pagina[0])
