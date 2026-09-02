# Reservas API — Clase 10: Seguridad y Pruebas

Aplicación CRUD básica de **reservas de mesa para 3 restaurantes** del grupo "Fresh Fork Restaurant Group" (el mismo cliente ficticio de RFP-001, ver `../docs/`) construida como material de estudio para la Semana 10 del curso: **cada mecanismo de las slides está implementado con código real y ejecutable**, no solo descrito.

**Este repo también contiene, a propósito, dos bugs reales** (una condición de carrera y un `ZeroDivisionError`) para que puedas ver, con tus propios ojos, los reportes que generan pytest, Playwright, Locust y PostHog cuando algo realmente falla — no solo cuando todo pasa. Ver [GUIA-DE-PRUEBAS.md § Bugs intencionales](./GUIA-DE-PRUEBAS.md#bugs-intencionales-para-ver-los-reportes-de-las-librerías-en-acción).

**La guía completa, tema por tema, con el comando exacto para probar cada uno, está en [GUIA-DE-PRUEBAS.md](./GUIA-DE-PRUEBAS.md).** Este README solo cubre cómo instalar y levantar todo.

## Stack

FastAPI (Python) · SQLAlchemy · PostgreSQL (con Row-Level Security real) · pytest · Playwright · Locust · PostHog (analítica + session replay).

## Requisitos

- Python 3.11+
- Docker (para Postgres local y para los tests de integración, que usan Testcontainers)

## Instalación

```bash
cd clase10-testing-seguridad
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium        # solo necesario para los tests E2E
cp .env.example .env
```

Si quieres analítica y session replay reales (opcional — todo funciona sin esto, ver sección 8 de la guía), agrega a tu `.env`:

```bash
POSTHOG_PROJECT_API_KEY=phc_...      # Project settings → Project API key (público, seguro de exponer al navegador)
POSTHOG_PERSONAL_API_KEY=phx_...     # (tu avatar) → Personal API keys — SECRETO, solo se usa del lado del servidor
```

## Levantar la aplicación

```bash
docker compose up -d               # Postgres local
python -m app.init_db              # crea tablas + política RLS + vista enmascarada
python -m app.seed_demo_data       # crea los 3 restaurantes + un gerente por restaurante
uvicorn app.main:app --reload
```

Abre <http://localhost:8000> (redirige a `/login.html`). Puedes iniciar sesión con cualquiera de los 3 gerentes que crea el seed (`gerente@fresh-fork-downtown.com` / `Segura123!`, y lo mismo para `-uptown` y `-riverside`), registrarte desde ahí, o por API:

```bash
curl -X POST http://localhost:8000/auth/registro \
  -H "Content-Type: application/json" \
  -d '{"restaurante":"fresh-fork-downtown","email":"demo@puy.com","password":"Segura123!","rol":"gerente"}'
```

## Correr las pruebas

Cada capa de la pirámide de pruebas (slide 5) es un comando separado — ver por qué en [GUIA-DE-PRUEBAS.md](./GUIA-DE-PRUEBAS.md#0-antes-de-empezar-por-qué-cada-suite-es-un-comando-aparte):

```bash
pytest tests/unit                                          # rápidas, sin Docker
pytest tests/integration                                   # necesita Docker corriendo
uvicorn app.main:app &  # servidor real, en otra terminal
pytest tests/e2e --base-url=http://localhost:8000 --html=report.html --self-contained-html
locust -f loadtest/locustfile.py --host http://localhost:8000  # carga, UI en :8089
```

`--html=report.html` (de `pytest-html`) genera un reporte visual con los resultados — uno de los "reportes generados por las librerías" que vale la pena ver, además de la salida de la terminal.

## Estructura

```
app/                    código de la aplicación (FastAPI)
  security/             passwords, jwt, rate_limit, masking, oauth
  routers/               auth.py, reservas.py, admin.py
  rls.sql                 política de Row-Level Security + vista enmascarada (slides 22-23)
  seed_demo_data.py       crea los 3 restaurantes de la demo + un gerente por cada uno
static/                 frontend mínimo (HTML/JS) — login, registro, dashboard CRUD, analytics.js (PostHog)
tests/
  unit/                  slide 6 — lógica aislada, sin BD
  integration/           slide 7 — BD real desechable (Testcontainers)
  e2e/                   slide 9/10 — Playwright contra un servidor real
loadtest/                slide 27 — Locust (reproduce el Bug intencional #1 bajo carga real)
docs/security-architecture.md   diagrama, flujos OAuth, TDD paso a paso, Cognito/Azure AD, rúbrica de Entrega 2, bugs intencionales
```
