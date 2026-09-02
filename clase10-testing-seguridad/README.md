# Cuentas API — Clase 10: Seguridad y Pruebas

Aplicación CRUD básica (staff de una organización gestiona **cuentas** — pensada como un ejemplo del dominio financiero: conciliación bancaria / fondos de pensiones) construida como material de estudio para la Semana 10 del curso: **cada mecanismo de las slides está implementado con código real y ejecutable**, no solo descrito.

**La guía completa, tema por tema, con el comando exacto para probar cada uno, está en [GUIA-DE-PRUEBAS.md](./GUIA-DE-PRUEBAS.md).** Este README solo cubre cómo instalar y levantar todo.

## Stack

FastAPI (Python) · SQLAlchemy · PostgreSQL (con Row-Level Security real) · pytest · Playwright · Locust.

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

## Levantar la aplicación

```bash
docker compose up -d               # Postgres local
python -m app.init_db              # crea tablas + política RLS + vista enmascarada
uvicorn app.main:app --reload
```

Abre <http://localhost:8000> (redirige a `/login.html`). Puedes registrarte desde ahí, o por API:

```bash
curl -X POST http://localhost:8000/auth/registro \
  -H "Content-Type: application/json" \
  -d '{"organizacion":"fresh-fork","email":"demo@puy.com","password":"Segura123!","rol":"admin"}'
```

## Correr las pruebas

Cada capa de la pirámide de pruebas (slide 5) es un comando separado — ver por qué en [GUIA-DE-PRUEBAS.md](./GUIA-DE-PRUEBAS.md#0-antes-de-empezar-por-qué-cada-suite-es-un-comando-aparte):

```bash
pytest tests/unit                                          # rápidas, sin Docker
pytest tests/integration                                   # necesita Docker corriendo
uvicorn app.main:app &  # servidor real, en otra terminal
pytest tests/e2e --base-url=http://localhost:8000           # necesita el servidor arriba
locust -f loadtest/locustfile.py --host http://localhost:8000  # carga, UI en :8089
```

## Estructura

```
app/                    código de la aplicación (FastAPI)
  security/             passwords, jwt, rate_limit, masking, oauth
  routers/               auth.py, accounts.py
  rls.sql                 política de Row-Level Security + vista enmascarada (slides 22-23)
static/                 frontend mínimo (HTML/JS) — login, registro, dashboard CRUD
tests/
  unit/                  slide 6 — lógica aislada, sin BD
  integration/           slide 7 — BD real desechable (Testcontainers)
  e2e/                   slide 9/10 — Playwright contra un servidor real
loadtest/                slide 27 — Locust
docs/security-architecture.md   diagrama, flujos OAuth, TDD paso a paso, Cognito/Azure AD, rúbrica de Entrega 2
```
