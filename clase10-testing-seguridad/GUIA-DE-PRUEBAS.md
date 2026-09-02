# Guía de pruebas — Semana 10: Seguridad y Pruebas

Un tema por sección, en el mismo orden que las slides. Cada uno dice **qué es**, **dónde está implementado en este repo**, y el **comando o pasos exactos** para verificarlo tú mismo. Usa esto como guion para la sustentación individual (slide 25: cada integrante explica, con criterio propio, la prueba o el mecanismo que implementó).

Antes de correr nada:

```bash
cd clase10-testing-seguridad
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

---

## 0. Antes de empezar: por qué cada suite es un comando aparte

`pytest` por sí solo (sin argumentos) corre **solo** `tests/unit` — así lo fija `pytest.ini`. Integración y E2E se invocan aparte (`pytest tests/integration`, `pytest tests/e2e --base-url=...`) por dos razones, no solo por costo/velocidad (slide 5):

1. **Técnica**: los tests de integración fijan `DATABASE_URL` hacia un contenedor Postgres desechable *antes* de que nada importe `app.config`/`app.database` (ver el comentario al inicio de `tests/integration/conftest.py`). Si unit e integración corrieran en el mismo proceso, el orden de importación entre archivos podría romper eso silenciosamente.
2. **Pedagógica**: coincide exactamente con la pirámide — la suite rápida corre todo el tiempo; las lentas y costosas se corren aparte, con su propio entorno.

---

## 1. Por qué probamos el software (slide 4)

Sin código de producto propio que "romper", la evidencia aquí es la suite misma: **34 pruebas automatizadas** (17 unitarias + 16 de integración + 3 E2E) que documentan, en código ejecutable, exactamente qué debe hacer el sistema. Corre todo y confirma:

```bash
pytest tests/unit -v          # 17 passed
pytest tests/integration -v   # 16 passed (requiere Docker)
```

## 2. La pirámide de pruebas (slide 5)

| Capa | Dónde | Comando | Qué necesita |
|---|---|---|---|
| Unitarias | `tests/unit/` | `pytest tests/unit` | nada — corren en ~2s |
| Integración | `tests/integration/` | `pytest tests/integration` | Docker corriendo (Testcontainers levanta Postgres real) |
| E2E | `tests/e2e/` | `pytest tests/e2e --base-url=http://localhost:8000` | servidor real (`uvicorn`) + Postgres reales corriendo |
| Carga | `loadtest/locustfile.py` | `locust -f loadtest/locustfile.py --host http://localhost:8000` | servidor real corriendo |

Nota cómo el conteo de pruebas baja mientras la infraestructura que necesitan sube — eso es la pirámide.

## 3. Pruebas unitarias (slide 6)

**Dónde:** `tests/unit/test_passwords.py`, `test_jwt.py`, `test_rate_limit.py`, `test_masking.py`. Cada test sigue el patrón **Arrange-Act-Assert**, con los tres pasos comentados explícitamente.

```bash
pytest tests/unit -v
```

`test_rate_limit.py` es el ejemplo más claro de "rápidas, deterministas, independientes": usa un reloj falso (`FakeClock`) inyectado en vez de `time.sleep()`, así que probar "el límite se resetea después de 10 segundos" toma microsegundos, no 10 segundos reales.

## 4. Pruebas de integración (slide 7)

**Dónde:** `tests/integration/`. `conftest.py` levanta un contenedor Postgres real y desechable con **Testcontainers** (exactamente la herramienta que menciona la slide), no un mock.

```bash
pytest tests/integration -v
```

El ejemplo típico de la slide — "probar que POST /orders inserta el registro y responde 201" — es literalmente `test_post_cuentas_inserts_a_row_and_responds_201` en `test_accounts_crud.py`.

## 5. TDD: Desarrollo Guiado por Pruebas (slide 8)

**Dónde:** `app/security/masking.py` + `tests/unit/test_masking.py`. Para practicar el ciclo tú mismo:

1. **RED** — comenta el cuerpo de `enmascarar_numero_cuenta` (deja solo `pass`) y corre `pytest tests/unit/test_masking.py` → las 3 pruebas fallan.
2. **GREEN** — escribe el mínimo código para que pasen, una por una.
3. **REFACTOR** — con las 3 en verde, simplifica sin romperlas (por ejemplo, unifica los dos `return`).

Detalle completo en [docs/security-architecture.md § TDD paso a paso](./docs/security-architecture.md#tdd-paso-a-paso).

## 6-7. End-to-End con Playwright (slides 9-10)

**Dónde:** `tests/e2e/test_login_flow.py`, usando `pytest-playwright` (la API Python de Playwright — mismo motor que el ejemplo JS/TS de la slide, misma semántica: navega, llena campos por id, hace clic, verifica un elemento visible).

```bash
docker compose up -d && python -m app.init_db
uvicorn app.main:app &
playwright install chromium   # una sola vez
pytest tests/e2e --base-url=http://localhost:8000 -v
```

`static/login.html` reproduce el escenario exacto de la slide 10: campos `#email`/`#password`, botón `button[type="submit"]`, y un `#dashboard` que se hace visible tras el login.

## 8. PostHog: Analítica de Producto (slide 11)

**Dónde:** `app/analytics.py`, con `capture()` llamado desde `app/routers/auth.py` (`registro`, `login`) y `app/routers/accounts.py` (`crear_cuenta`) — los 2-3 eventos clave que sugiere la slide.

**Cómo probarlo sin cuenta de PostHog:** deja `POSTHOG_API_KEY` vacío en `.env` (el default) y observa el log al registrarte/loguearte/crear una cuenta:

```bash
uvicorn app.main:app --log-level info
# ... en otra terminal, dispara /auth/registro ...
# verás: "posthog(no-op): event=registro distinct_id=1 properties=..."
```

**Con una cuenta real de PostHog:** pon tu `POSTHOG_API_KEY` en `.env` y los mismos eventos llegarán al proyecto — session replay y feature flags se configuran desde el dashboard de PostHog, no desde este código.

## 9. Autenticación y Autorización (slide 12)

**Dónde:** `app/deps.py`. `get_current_claims` (AuthN — decodifica y valida el JWT) es una dependencia distinta de `require_role(...)` (AuthZ — decide si ese usuario ya identificado puede hacer *esto*).

```bash
curl -i http://localhost:8000/auth/me                                    # 401 — ni siquiera hay identidad
curl -i http://localhost:8000/cuentas/1 -X DELETE -H "Authorization: Bearer $TOKEN_USUARIO"  # 403 — identificado, pero sin permiso
```

Pruebas automatizadas: `tests/integration/test_auth_flow.py::test_protected_endpoint_without_a_token_is_rejected` (AuthN) y `test_accounts_crud.py::test_only_admin_can_delete_a_cuenta` (AuthZ).

## 10-11. AWS Cognito / Azure AD (Entra ID) (slides 13-14)

Este repo **no está conectado a un tenant real** (requeriría una cuenta AWS/Azure del estudiante) — lo que sí implementa es el código de validación real que consumiría uno, en `app/security/jwt.py`: cuando `AUTH_PROVIDER=cognito` o `AUTH_PROVIDER=azure`, `decode_and_validate_token()` descarga las llaves públicas del emisor (JWKS) y valida la firma RS256 contra ellas, en vez del secreto compartido HS256 que usa `AUTH_PROVIDER=local` (el modo por defecto, usado por toda la suite de pruebas de este repo).

**Para conectarlo a un Cognito User Pool real:**

```bash
# .env
AUTH_PROVIDER=cognito
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
```

y usar el Hosted UI de Cognito (o el SDK) para que el frontend obtenga el JWT, en vez de `POST /auth/login`. Ver [docs/security-architecture.md § Cognito y Azure AD](./docs/security-architecture.md#cognito-y-azure-ad-cómo-conectar-un-tenant-real) para Azure AD y el detalle de qué cambia.

## 12. Cognito vs. Azure AD (slide 15)

Puramente comparativo — no hay código que probar aquí. Ver la tabla y cuándo usar cada uno en [docs/security-architecture.md](./docs/security-architecture.md#cognito-y-azure-ad-cómo-conectar-un-tenant-real).

## 13. JWT: Estructura y Validación (slide 16)

**Dónde:** `app/security/jwt.py` + `tests/unit/test_jwt.py` (6 pruebas: token válido, expirado, firma alterada, `iss`/`aud` incorrectos, y una que decodifica el payload sin la llave para demostrar que no está encriptado).

```bash
pytest tests/unit/test_jwt.py -v
```

**Verlo con tus propios ojos:** loguéate, copia el `access_token`, y pégalo en <https://jwt.io> (sin la llave, jwt.io ya te muestra el payload — esa es exactamente la lección de la slide).

## 14. Flujo de Autenticación con JWT (slide 17 de las slides — no confundir con la sección 17 de esta guía)

Diagrama completo en [docs/security-architecture.md](./docs/security-architecture.md#arquitectura-de-seguridad-end-to-end). En este repo: `static/login.html` → `POST /auth/login` (emite JWT) → cada request subsiguiente pasa `Authorization: Bearer <token>` → `app/deps.py` lo valida antes de tocar la base de datos.

## 15. OAuth 2.0: Flujos de Autorización (slide 18)

**Dónde:** `app/routers/auth.py`. `POST /auth/login` es el análogo simplificado, educativo, del flujo **Authorization Code + PKCE** (una persona presenta credenciales, recibe tokens) — sin el redirect real ni el intercambio de código de un solo uso, que necesitan una página de login hospedada aparte (ver por qué en el docstring del endpoint). `POST /auth/token` implementa **Client Credentials** completo y real (servicio-a-servicio, sin humano):

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id":"reporting-service","client_secret":"dev-only-client-secret"}'
```

Pruebas: `tests/integration/test_auth_flow.py::test_client_credentials_grant_issues_a_service_token` y `..._rejects_a_wrong_secret`.

## 16. Manejo Seguro de Credenciales (slide 19)

**Dónde:** `app/config.py` (todo viene de variables de entorno, ningún valor hardcodeado en la lógica), `.env.example` (plantilla sin secretos reales), `.gitignore` (`.env` nunca se commitea).

**Cómo verificarlo:**

```bash
git status              # .env no debe aparecer nunca aquí (está en .gitignore)
grep -rn "password\|secret\|Segura123" app/ --include="*.py" | grep -v "app/config.py\|app/security"
# no debería devolver contraseñas ni secretos reales, solo nombres de campos/parámetros
```

En producción, `.env` se reemplaza por AWS Secrets Manager / Parameter Store — no hay código de eso aquí porque es configuración de infraestructura, no de la aplicación (ver la arquitectura AWS de este mismo repo en `../docs/diagramas/arquitectura-aws.md`, que ya usa Secrets Manager para las credenciales de RDS).

## 17. Rate Limiting (slide 20)

**Dónde:** `app/security/rate_limit.py` (lógica pura, ventana fija) + `app/main.py` (aplicado a `/auth/login`).

```bash
pytest tests/unit/test_rate_limit.py -v          # la lógica del limitador, aislada
pytest tests/integration/test_rate_limit_integration.py -v   # el middleware completo, por HTTP

# o a mano, con el servidor corriendo (límite por defecto: 5/60s):
for i in $(seq 1 7); do curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" -d '{"email":"x@x.com","password":"x"}'; done
# los últimos deberían devolver 429
```

## 18. Encriptación: En Tránsito y en Reposo (slide 21)

**Contraseñas (lo único que este repo puede demostrar con código):** `app/security/passwords.py` usa bcrypt — nunca texto plano, nunca "encriptado" (irreversible por diseño).

```bash
pytest tests/unit/test_passwords.py -v
```

**TLS y encriptación en reposo** son configuración de infraestructura (terminación TLS en el load balancer/CloudFront, `AWS KMS` en RDS/S3) — no hay nada que un `pytest` local pueda verificar; están documentadas, con ejemplo real, en `../docs/diagramas/arquitectura-aws.md` de este mismo repositorio (CloudFront + RDS del proyecto Fresh Fork).

## 19. Row-Level Security en PostgreSQL (slide 22)

**Dónde:** `app/rls.sql` — la política es prácticamente copy-paste de la slide, adaptada a `cuentas`/`organizacion_id`.

```bash
pytest tests/integration/test_accounts_crud.py::test_rls_blocks_cross_tenant_reads_even_with_no_where_clause_at_all -v
```

Esa prueba es la demostración más fuerte posible: hace `SELECT titular FROM cuentas` **sin ningún WHERE**, como el rol de la organización B, y solo recibe la fila de B — la base de datos, no el código de la aplicación, es quien filtra.

**A mano, con `psql` contra el Postgres de `docker compose`:**

```bash
docker compose exec db psql -U cuentas_app -d cuentas_db
SET app.org_id = '1';
SELECT * FROM cuentas;          -- solo filas de la organización 1
SET app.org_id = '2';
SELECT * FROM cuentas;          -- ahora solo filas de la organización 2, misma sesión, mismo rol
```

Ver también [docs/security-architecture.md § El superusuario invisible](./docs/security-architecture.md#el-superusuario-invisible-un-hallazgo-real-de-este-repo) — un problema real que este repo encontró mientras escribía estas pruebas y que vale la pena entender.

## 20. Column Masking (slide 23)

**Dos implementaciones, a propósito:** la vista SQL `cuentas_enmascaradas` en `app/rls.sql` (idéntica a la slide) y la función pura `enmascarar_numero_cuenta` en `app/security/masking.py` (la misma regla, en Python, testeable sin base de datos).

```bash
pytest tests/unit/test_masking.py -v                                    # la regla, aislada
pytest tests/integration/test_accounts_crud.py -k masked -v             # la vista, vía la API
```

```bash
# a mano
curl -s http://localhost:8000/cuentas -H "Authorization: Bearer $TOKEN_ROL_USUARIO" | jq '.[0].numero_cuenta'
# "**** **** **** 1234"
curl -s http://localhost:8000/cuentas -H "Authorization: Bearer $TOKEN_ROL_ADMIN" | jq '.[0].numero_cuenta'
# "1111222233331234"
```

## 21. Arquitectura de Seguridad End-to-End (slide 24)

Diagrama completo (equivalente a esta app) en [docs/security-architecture.md](./docs/security-architecture.md#arquitectura-de-seguridad-end-to-end).

## 22. Qué Necesitas para Entrega 2 (slide 25)

Mapeo rúbrica → evidencia concreta en este repo: [docs/security-architecture.md § Rúbrica de Entrega 2](./docs/security-architecture.md#rúbrica-de-entrega-2--dónde-está-la-evidencia).

## 23. Actividad: Demo de Seguridad de Datos y Autenticación (slide 26)

La actividad pide: login con Cognito/Azure AD, generar y validar un JWT, y cubrirlo con al menos una prueba unitaria y una de integración. Este repo ya lo cumple con el proveedor local (JWT real, mismo formato que emitiría Cognito/Azure):

- Unitaria: `tests/unit/test_jwt.py`
- Integración: `tests/integration/test_auth_flow.py::test_registro_then_login_then_access_protected_endpoint`

Para hacerlo con un proveedor real, sigue la sección 10-11 de esta guía y sustituye `POST /auth/login` por el Hosted UI de Cognito/Azure en `static/login.html`.

## LOAD TESTS (slide 27)

**Dónde:** `loadtest/locustfile.py`.

```bash
uvicorn app.main:app &
locust -f loadtest/locustfile.py --host http://localhost:8000
# abre http://localhost:8089, define usuarios y spawn rate, observa las estadísticas en vivo
```

**Qué encontramos corriendo este load test:** con varios usuarios registrándose "concurrentemente" bajo el mismo nombre de organización, el `get-or-create` de `Organizacion` en `app/routers/auth.py` tenía una condición de carrera — dos requests podían ver "no existe" al mismo tiempo e intentar insertarla ambas, y la segunda fallaba con un `500` sin manejar. El fix (capturar el `IntegrityError` y releer la fila que ganó la carrera) está en el código y cubierto por `tests/integration/test_auth_flow.py::test_two_users_registering_under_the_same_organizacion_share_its_id`. Esto es exactamente lo que un load test debe hacer: encontrar bugs que ninguna prueba unitaria o de integración secuencial iba a encontrar.

También verás `429 Too Many Requests` en las estadísticas de `/auth/login` una vez hay suficientes usuarios concurrentes — el rate limiter (sección 17) funcionando bajo carga real, no solo en una prueba aislada.
