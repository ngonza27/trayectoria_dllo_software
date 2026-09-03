# Guía de pruebas — Semana 10: Seguridad y Pruebas

Un tema por sección, en el mismo orden que las slides. Cada uno dice **qué es**, **dónde está implementado en este repo**, y el **comando o pasos exactos** para verificarlo tú mismo. Usa esto como guion para la sustentación individual.

El dominio de esta demo: reservas de mesa para los **3 restaurantes** del grupo "Fresh Fork Restaurant Group" (`fresh-fork-downtown`, `fresh-fork-uptown`, `fresh-fork-riverside`) — cada restaurante es un tenant aislado por Row-Level Security (sección 19).

Antes de correr nada:

```bash
cd clase10-testing-seguridad
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Windows (PowerShell):**

```powershell
cd clase10-testing-seguridad
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

---

## 0. Antes de empezar: por qué cada suite es un comando aparte

`pytest` por sí solo (sin argumentos) corre **solo** `tests/unit` — así lo fija `pytest.ini`. Integración y E2E se invocan aparte (`pytest tests/integration`, `pytest tests/e2e --base-url=...`) por dos razones, no solo por costo/velocidad:

1. **Técnica**: los tests de integración fijan `DATABASE_URL` hacia un contenedor Postgres desechable *antes* de que nada importe `app.config`/`app.database` (ver el comentario al inicio de `tests/integration/conftest.py`). Si unit e integración corrieran en el mismo proceso, el orden de importación entre archivos podría romper eso silenciosamente.
2. **Pedagógica**: coincide exactamente con la pirámide — la suite rápida corre todo el tiempo; las lentas y costosas se corren aparte, con su propio entorno.

### Notas para Windows (PowerShell)

Este repo se escribió pensando en bash/zsh (macOS/Linux). La alternativa más simple en Windows es correr todo dentro de **WSL2** o **Git Bash**, donde cada comando de esta guía funciona tal cual. Si prefieres PowerShell nativo, estos son los patrones que se repiten y su equivalente — de aquí en adelante, cada bloque no trivial trae su versión PowerShell al lado:

| Patrón bash | Equivalente PowerShell |
|---|---|
| `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |
| `cmd1 && cmd2` | igual en PowerShell 7+; en Windows PowerShell 5.1, ejecuta cada uno en su propia línea |
| `cmd &` (segundo plano) | más simple: abre una terminal nueva y corre el comando ahí |
| `curl ...` | usa `curl.exe ...` explícito — `curl` a secas es un alias de `Invoke-WebRequest`, que no soporta `-s`/`-o`/`-w`/`-d` igual |
| `... \| jq -r .campo` | instala `jq` (`winget install jqlang.jq`) — el pipe funciona igual — o usa `(... \| ConvertFrom-Json).campo` |
| `for i in $(seq 1 7); do ...; done` | `1..7 \| ForEach-Object { ... }` |
| `grep -rn "patrón" carpeta/` | `Select-String -Path carpeta\* -Pattern "patrón" -Recurse` |
| línea terminada en `\` (continuación) | usa el backtick `` ` `` en PowerShell, o pon el comando en una sola línea |

---

## 1. Por qué probamos el software

Sin código de producto propio que "romper", la evidencia aquí es la suite misma: pruebas automatizadas (17 unitarias + 18 de integración + 4 E2E) que documentan, en código ejecutable, exactamente qué debe hacer el sistema — **incluyendo dos casos donde documentan, a propósito, que algo está roto** (ver la sección "Bugs intencionales" al final). Corre todo y confirma:

```bash
pytest tests/unit -v          # 17 passed
pytest tests/integration -v   # 18 passed (uno de ellos, el del Bug intencional #2, pasa demostrando el bug con pytest.raises — requiere Docker)
```

## 2. La pirámide de pruebas

| Capa | Dónde | Comando | Qué necesita |
|---|---|---|---|
| Unitarias | `tests/unit/` | `pytest tests/unit` | nada — corren en ~2s |
| Integración | `tests/integration/` | `pytest tests/integration` | Docker corriendo (Testcontainers levanta Postgres real) |
| E2E | `tests/e2e/` | `pytest tests/e2e --base-url=http://localhost:8000` | servidor real (`uvicorn`) + Postgres reales corriendo |
| Carga | `loadtest/locustfile.py` | `locust -f loadtest/locustfile.py --host http://localhost:8000` | servidor real corriendo |

Nota cómo el conteo de pruebas baja mientras la infraestructura que necesitan sube — eso es la pirámide.

## 3. Pruebas unitarias

**Dónde:** `tests/unit/test_passwords.py`, `test_jwt.py`, `test_rate_limit.py`, `test_masking.py`. Cada test sigue el patrón **Arrange-Act-Assert**, con los tres pasos comentados explícitamente.

```bash
pytest tests/unit -v
```

`test_rate_limit.py` es el ejemplo más claro de "rápidas, deterministas, independientes": usa un reloj falso (`FakeClock`) inyectado en vez de `time.sleep()`, así que probar "el límite se resetea después de 10 segundos" toma microsegundos, no 10 segundos reales.

## 4. Pruebas de integración

**Dónde:** `tests/integration/`. `conftest.py` levanta un contenedor Postgres real y desechable con **Testcontainers**, no un mock.

```bash
pytest tests/integration -v
```

El ejemplo típico — "probar que POST /orders inserta el registro y responde 201" — es literalmente `test_post_reservas_inserts_a_row_and_responds_201` en `test_reservas_crud.py`.

## 5-6. End-to-End con Playwright

**Dónde:** `tests/e2e/test_login_flow.py` (flujo feliz) y `tests/e2e/test_reportes_de_errores.py` (el Bug intencional #2, ver más abajo), usando `pytest-playwright` (la API Python de Playwright — mismo motor que el ejemplo JS/TS, misma semántica: navega, llena campos por id, hace clic, verifica un elemento visible).

```bash
docker compose up -d && python -m app.init_db && python -m app.seed_demo_data
uvicorn app.main:app &
playwright install chromium   # una sola vez
pytest tests/e2e --base-url=http://localhost:8000 -v --html=report.html --self-contained-html
```

**Windows (PowerShell):** corre `uvicorn` en una terminal separada en vez de usar `&`:

```powershell
docker compose up -d
python -m app.init_db
python -m app.seed_demo_data
uvicorn app.main:app   # deja esta terminal corriendo

# en OTRA terminal (con el venv activado):
playwright install chromium   # una sola vez
pytest tests/e2e --base-url=http://localhost:8000 -v --html=report.html --self-contained-html
```

`static/login.html` reproduce el escenario: campos `#email`/`#password`, botón `button[type="submit"]`, y un `#dashboard` que se hace visible tras el login. `--html=report.html` genera un reporte visual de la corrida (otra de las "librerías" cuyo reporte vale la pena ver, junto con Locust y PostHog más abajo).

## 7. PostHog: Analítica de Producto y Session Replay

**Dónde:**
- Backend: `app/services/analytics_service.py` (`capture()`, llamado desde `app/services/auth_service.py` — `registrar`/`login` — y `app/services/reservas_service.py` — `crear_reserva`).
- Frontend: `static/analytics.js`, incluido en cada página HTML. Inicializa `posthog-js` con la llave que expone `GET /public-config` (`app/main.py`) y activa `capture_exceptions: true` — autocaptura de errores no manejados y session replay.

**Una sola llave:** Project API key (`phc_...`), **pública** — vive en `.env` → `POSTHOG_PROJECT_API_KEY` y se sirve al navegador vía `GET /public-config`. Sirve para capturar eventos (server y cliente) y grabar session replay.

**Cómo probarlo sin cuenta de PostHog:** deja la llave vacía en `.env` (el default) y observa el log al registrarte/loguearte/crear una reserva:

```bash
uvicorn app.main:app --log-level info
# ... en otra terminal, dispara /auth/registro ...
# verás: "posthog(no-op): event=registro distinct_id=1 properties=..."
```

**Con una cuenta real de PostHog** (pon `POSTHOG_PROJECT_API_KEY` en `.env`, y activa **Record user sessions** en Settings → Recordings del proyecto):

1. Levanta la app, abre `http://localhost:8000/login.html` en un navegador real (no en modo headless) y regístrate/loguéate — deberías ver la sesión aparecer en PostHog → **Activity** casi en tiempo real.
2. Ve al dashboard: como el restaurante es nuevo, dispara el **Bug intencional #2** (abajo) — PostHog captura el `TypeError` como un evento `$exception` (**Error tracking**) y graba la sesión completa (**Session replay**), reproducible fotograma a fotograma con el error resaltado en el momento exacto en que ocurrió, visible directamente en el dashboard de PostHog.

## 8. Autenticación y Autorización

**Dónde:** `app/deps.py`. `get_current_claims` (AuthN — decodifica y valida el JWT) es una dependencia distinta de `require_role(...)` (AuthZ — decide si ese usuario ya identificado puede hacer *esto*).

```bash
curl -i http://localhost:8000/auth/me                                    # 401 — ni siquiera hay identidad
curl -i http://localhost:8000/reservas/1 -X DELETE -H "Authorization: Bearer $TOKEN_MESERO"  # 403 — identificado, pero sin permiso
```

**Windows (PowerShell):**

```powershell
curl.exe -i http://localhost:8000/auth/me                                    # 401 — ni siquiera hay identidad
curl.exe -i http://localhost:8000/reservas/1 -X DELETE -H "Authorization: Bearer $env:TOKEN_MESERO"  # 403 — identificado, pero sin permiso
```

Pruebas automatizadas: `tests/integration/test_auth_flow.py::test_protected_endpoint_without_a_token_is_rejected` (AuthN) y `test_reservas_crud.py::test_only_gerente_can_cancel_a_reserva` (AuthZ).

## 9-10. AWS Cognito / Azure AD (Entra ID)

Este repo **no está conectado a un tenant real** (requeriría una cuenta AWS/Azure del estudiante) — lo que sí implementa es el código de validación real que consumiría uno, en `app/security/jwt.py`: cuando `AUTH_PROVIDER=cognito` o `AUTH_PROVIDER=azure`, `decode_and_validate_token()` descarga las llaves públicas del emisor (JWKS) y valida la firma RS256 contra ellas, en vez del secreto compartido HS256 que usa `AUTH_PROVIDER=local` (el modo por defecto, usado por toda la suite de pruebas de este repo).

**Para conectarlo a un Cognito User Pool real:**

```bash
# .env
AUTH_PROVIDER=cognito
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
```

y usar el Hosted UI de Cognito (o el SDK) para que el frontend obtenga el JWT, en vez de `POST /auth/login`. Ver [docs/security-architecture.md § Cognito y Azure AD](./docs/security-architecture.md#cognito-y-azure-ad-cómo-conectar-un-tenant-real) para Azure AD y el detalle de qué cambia.

## 11. Cognito vs. Azure AD

Puramente comparativo — no hay código que probar aquí. Ver la tabla y cuándo usar cada uno en [docs/security-architecture.md](./docs/security-architecture.md#cognito-y-azure-ad-cómo-conectar-un-tenant-real).

## 12. JWT: Estructura y Validación

**Dónde:** `app/security/jwt.py` + `tests/unit/test_jwt.py` (6 pruebas: token válido, expirado, firma alterada, `iss`/`aud` incorrectos, y una que decodifica el payload sin la llave para demostrar que no está encriptado).

```bash
pytest tests/unit/test_jwt.py -v
```

**Verlo con tus propios ojos:** loguéate, copia el `access_token`, y pégalo en <https://jwt.io> (sin la llave, jwt.io ya te muestra el payload).

## 13. Flujo de Autenticación con JWT

Diagrama completo en [docs/security-architecture.md](./docs/security-architecture.md#arquitectura-de-seguridad-end-to-end). En este repo: `static/login.html` → `POST /auth/login` (emite JWT) → cada request subsiguiente pasa `Authorization: Bearer <token>` → `app/deps.py` lo valida antes de tocar la base de datos.

## 14. OAuth 2.0: Flujos de Autorización

**Dónde:** `app/routes/auth_routes.py` y `app/services/auth_service.py`. `POST /auth/login` es el análogo simplificado, educativo, del flujo **Authorization Code + PKCE** (una persona presenta credenciales, recibe tokens) — sin el redirect real ni el intercambio de código de un solo uso, que necesitan una página de login hospedada aparte (ver por qué en el docstring del endpoint). `POST /auth/token` implementa **Client Credentials** completo y real (servicio-a-servicio, sin humano):

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id":"reporting-service","client_secret":"dev-only-client-secret"}'
```

**Windows (PowerShell):**

```powershell
curl.exe -X POST http://localhost:8000/auth/token `
  -H "Content-Type: application/json" `
  -d '{"client_id":"reporting-service","client_secret":"dev-only-client-secret"}'
```

Pruebas: `tests/integration/test_auth_flow.py::test_client_credentials_grant_issues_a_service_token` y `..._rejects_a_wrong_secret`.

## 15. Manejo Seguro de Credenciales

**Dónde:** `app/config.py` (todo viene de variables de entorno, ningún valor hardcodeado en la lógica), `.env.example` (plantilla sin secretos reales), `.gitignore` (`.env` nunca se commitea).

**Cómo verificarlo:**

```bash
git status              # .env no debe aparecer nunca aquí (está en .gitignore)
grep -rn "password\|secret\|Segura123\|phc_\|phx_" app/ --include="*.py" | grep -v "app/config.py\|app/security"
# no debería devolver contraseñas ni llaves reales, solo nombres de campos/parámetros
```

**Windows (PowerShell):**

```powershell
git status              # .env no debe aparecer nunca aquí (está en .gitignore)
Select-String -Path app\**\*.py -Pattern "password|secret|Segura123|phc_|phx_" | Where-Object { $_.Path -notmatch "app\\config\.py|app\\security" }
# no debería devolver contraseñas ni llaves reales, solo nombres de campos/parámetros
```

Esto aplica también a la llave de PostHog de la sección 7: se sirve desde el backend vía `/public-config` (nunca hardcodeada en `static/`), y es la única llave que este repo maneja (pública, segura de exponer al navegador).

En producción, `.env` se reemplaza por AWS Secrets Manager / Parameter Store — no hay código de eso aquí porque es configuración de infraestructura, no de la aplicación (ver la arquitectura AWS de este mismo repo en `../docs/diagramas/arquitectura-aws.md`, que ya usa Secrets Manager para las credenciales de RDS).

## 16. Rate Limiting

**Dónde:** `app/security/rate_limit.py` (lógica pura, ventana fija) + `app/main.py` (aplicado a `/auth/login`).

```bash
pytest tests/unit/test_rate_limit.py -v          # la lógica del limitador, aislada
pytest tests/integration/test_rate_limit_integration.py -v   # el middleware completo, por HTTP

# o a mano, con el servidor corriendo (límite por defecto: 5/60s):
for i in $(seq 1 7); do curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" -d '{"email":"x@x.com","password":"x"}'; done
# los últimos deberían devolver 429
```

**Windows (PowerShell):**

```powershell
1..7 | ForEach-Object {
  curl.exe -s -o NUL -w "%{http_code}`n" -X POST http://localhost:8000/auth/login `
    -H "Content-Type: application/json" -d '{"email":"x@x.com","password":"x"}'
}
# los últimos deberían devolver 429
```

## 17. Encriptación: En Tránsito y en Reposo

**Contraseñas (lo único que este repo puede demostrar con código):** `app/security/passwords.py` usa bcrypt — nunca texto plano, nunca "encriptado" (irreversible por diseño).

```bash
pytest tests/unit/test_passwords.py -v
```

**TLS y encriptación en reposo** son configuración de infraestructura (terminación TLS en el load balancer/CloudFront, `AWS KMS` en RDS/S3) — no hay nada que un `pytest` local pueda verificar; están documentadas, con ejemplo real, en `../docs/diagramas/arquitectura-aws.md` de este mismo repositorio (CloudFront + RDS del proyecto Fresh Fork).

## 18. Row-Level Security en PostgreSQL

**Dónde:** `app/rls.sql` — la política es prácticamente adaptada a `reservas`/`restaurante_id`.

```bash
pytest tests/integration/test_reservas_crud.py::test_rls_blocks_cross_tenant_reads_even_with_no_where_clause_at_all -v
```

Esa prueba es la demostración más fuerte posible: hace `SELECT cliente_nombre FROM reservas` **sin ningún WHERE**, como el rol del restaurante B, y solo recibe la fila de B — la base de datos, no el código de la aplicación, es quien filtra.

**A mano, con `psql` contra el Postgres de `docker compose`:**

```bash
docker compose exec db psql -U reservas_app -d reservas_db
SET app.restaurante_id = '1';
SELECT * FROM reservas;          -- solo filas del restaurante 1
SET app.restaurante_id = '2';
SELECT * FROM reservas;          -- ahora solo filas del restaurante 2, misma sesión, mismo rol
```

Ver también [docs/security-architecture.md § El superusuario invisible](./docs/security-architecture.md#el-superusuario-invisible-un-hallazgo-real-de-este-repo) — un problema real que este repo encontró mientras escribía estas pruebas y que vale la pena entender.

## 19. Column Masking

**Dos implementaciones, a propósito:** la vista SQL `reservas_enmascaradas` en `app/rls.sql` y la función pura `enmascarar_telefono` en `app/security/masking.py` (la misma regla, en Python, testeable sin base de datos) — aquí aplicada al teléfono del cliente en vez de un número de cuenta.

```bash
pytest tests/unit/test_masking.py -v                                    # la regla, aislada
pytest tests/integration/test_reservas_crud.py -k masked -v             # la vista, vía la API
```

```bash
# a mano
curl -s http://localhost:8000/reservas -H "Authorization: Bearer $TOKEN_ROL_MESERO" | jq '.[0].telefono'
# "*** *** 4567"
curl -s http://localhost:8000/reservas -H "Authorization: Bearer $TOKEN_ROL_GERENTE" | jq '.[0].telefono'
# "+573001234567"
```

**Windows (PowerShell)** — sin `jq`, usando `ConvertFrom-Json`:

```powershell
(curl.exe -s http://localhost:8000/reservas -H "Authorization: Bearer $env:TOKEN_ROL_MESERO" | ConvertFrom-Json)[0].telefono
# "*** *** 4567"
(curl.exe -s http://localhost:8000/reservas -H "Authorization: Bearer $env:TOKEN_ROL_GERENTE" | ConvertFrom-Json)[0].telefono
# "+573001234567"
```

## 20. Arquitectura de Seguridad End-to-End

Diagrama completo (equivalente a esta app) en [docs/security-architecture.md](./docs/security-architecture.md#arquitectura-de-seguridad-end-to-end).

## 21. Qué Necesitas para Entrega 2

Mapeo rúbrica → evidencia concreta en este repo: [docs/security-architecture.md § Rúbrica de Entrega 2](./docs/security-architecture.md#rúbrica-de-entrega-2--dónde-está-la-evidencia).

## 22. Actividad: Demo de Seguridad de Datos y Autenticación

La actividad pide: login con Cognito/Azure AD, generar y validar un JWT, y cubrirlo con al menos una prueba unitaria y una de integración. Este repo ya lo cumple con el proveedor local (JWT real, mismo formato que emitiría Cognito/Azure):

- Unitaria: `tests/unit/test_jwt.py`
- Integración: `tests/integration/test_auth_flow.py::test_registro_then_login_then_access_protected_endpoint`

Para hacerlo con un proveedor real, sigue la sección 10-11 de esta guía y sustituye `POST /auth/login` por el Hosted UI de Cognito/Azure en `static/login.html`.

## LOAD TESTS

**Dónde:** `loadtest/locustfile.py`.

```bash
uvicorn app.main:app &
locust -f loadtest/locustfile.py --host http://localhost:8000
# abre http://localhost:8089, define usuarios y spawn rate, observa las estadísticas en vivo
```

**Windows (PowerShell):** corre `uvicorn` en su propia terminal y `locust` en otra:

```powershell
uvicorn app.main:app   # deja esta terminal corriendo

# en OTRA terminal:
locust -f loadtest/locustfile.py --host http://localhost:8000
# abre http://localhost:8089, define usuarios y spawn rate, observa las estadísticas en vivo
```

Ver la sección siguiente — este load test está diseñado a propósito para reproducir el Bug intencional #1.

---

## Bugs intencionales (para ver los reportes de las librerías en acción)

Esta demo deja **dos bugs reales, sin corregir, a propósito** — no son errores en el ejercicio, son el ejercicio: la meta es que veas cómo cada herramienta (pytest, Playwright, Locust, PostHog) *reporta* un fallo real, no solo que veas una suite en verde.

### Bug intencional #1 — condición de carrera en `POST /auth/registro`

**Dónde:** `app/services/auth_service.py`, el `get-or-create` de `Restaurante`. Si dos requests llegan casi al mismo tiempo pidiendo el mismo restaurante nuevo, ambos pueden ver "no existe todavía" y ambos intentan `INSERT`arlo — el segundo revienta con un `IntegrityError` de Postgres (violación de la restricción `UNIQUE` en `restaurantes.nombre`) que nadie captura, y Starlette lo convierte en un `500 Internal Server Error` real.

**Cómo verlo — el reporte de Locust:**

```bash
docker compose up -d && python -m app.init_db
uvicorn app.main:app &
locust -f loadtest/locustfile.py --host http://localhost:8000 \
    --users 30 --spawn-rate 30 --run-time 20s --headless
```

**Windows (PowerShell):**

```powershell
docker compose up -d
python -m app.init_db
uvicorn app.main:app   # deja esta terminal corriendo

# en OTRA terminal:
locust -f loadtest/locustfile.py --host http://localhost:8000 `
    --users 30 --spawn-rate 30 --run-time 20s --headless
```

`loadtest/locustfile.py` hace que **todos** los usuarios simulados se registren bajo el mismo restaurante (`"carga-comun"`) a propósito, para maximizar la contención. Con suficientes usuarios arrancando "al mismo tiempo" (spawn rate alto), la tabla de resumen final de Locust muestra `/auth/registro [POST]` con un `# Failures` mayor a 0, y la sección **Failures** de la UI web (`http://localhost:8089`) lista el mensaje exacto (`response.failure(...)` en el locustfile). Esto es exactamente lo que un load test debe hacer: encontrar bugs de concurrencia que ningún test unitario o de integración secuencial va a encontrar — `tests/integration/test_auth_flow.py::test_two_users_registering_under_the_same_restaurante_share_its_id` pasa porque es secuencial, no concurrente.

**El arreglo** (si quisieras corregirlo) es el patrón estándar: capturar el `IntegrityError`, hacer `rollback()`, y releer la fila que ganó la carrera — documentado, con el código exacto, en [docs/security-architecture.md § Bugs intencionales](./docs/security-architecture.md#bugs-intencionales-cómo-se-ven-en-cada-herramienta).

### Bug intencional #2 — `ZeroDivisionError` en `GET /reservas/resumen`

**Dónde:** `app/services/reservas_service.py`, `resumen_reservas()`: calcula `total_personas / len(reservas)` sin comprobar que la lista no esté vacía. Un restaurante recién registrado no tiene reservas todavía, así que el endpoint revienta con un `ZeroDivisionError` real — un `500` sin capturar.

**El frontend lo empeora a propósito:** `static/dashboard.html` → `cargarResumen()` no valida `response.ok` antes de leer el body. El `500` real de Starlette (sin `DEBUG`) es texto plano ("Internal Server Error"), no JSON — `await response.json()` revienta con un `SyntaxError` **no capturado** en el navegador al intentar parsearlo.

**Tres formas de verlo, tres reportes distintos:**

1. **El traceback crudo de la librería del servidor** (uvicorn/Starlette) — el más literal de "ver el reporte":
   ```bash
   uvicorn app.main:app --reload
   # en otra terminal, crea un restaurante nuevo y pide su resumen sin haber creado ninguna reserva:
   curl -s -X POST http://localhost:8000/auth/registro -H "Content-Type: application/json" \
     -d '{"restaurante":"demo-bug-2","email":"bug2@puy.com","password":"Segura123!"}' > /dev/null
   TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
     -d '{"email":"bug2@puy.com","password":"Segura123!"}' | jq -r .access_token)
   curl -i http://localhost:8000/reservas/resumen -H "Authorization: Bearer $TOKEN"
   # 500 Internal Server Error — y en la terminal de uvicorn, un traceback completo
   # terminando en "ZeroDivisionError: division by zero"
   ```

   **Windows (PowerShell):**
   ```powershell
   uvicorn app.main:app --reload   # deja esta terminal corriendo

   # en OTRA terminal, crea un restaurante nuevo y pide su resumen sin haber creado ninguna reserva:
   curl.exe -s -X POST http://localhost:8000/auth/registro -H "Content-Type: application/json" `
     -d '{"restaurante":"demo-bug-2","email":"bug2@puy.com","password":"Segura123!"}' | Out-Null
   $TOKEN = (curl.exe -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" `
     -d '{"email":"bug2@puy.com","password":"Segura123!"}' | ConvertFrom-Json).access_token
   curl.exe -i http://localhost:8000/reservas/resumen -H "Authorization: Bearer $TOKEN"
   # 500 Internal Server Error — y en la terminal de uvicorn, un traceback completo
   # terminando en "ZeroDivisionError: division by zero"
   ```
2. **pytest**, documentando el bug tal como se dejó: `tests/integration/test_reservas_crud.py::test_resumen_of_a_restaurante_with_no_reservas_hits_bug_intencional_2` — quita el `pytest.raises(ZeroDivisionError)` de ese test y verás el mismo traceback, esta vez en el reporte de pytest.
3. **Playwright + PostHog**, del lado del navegador: `tests/e2e/test_reportes_de_errores.py::test_dashboard_de_un_restaurante_nuevo_dispara_un_error_capturable_por_playwright` escucha `page.on("pageerror", ...)` — sin instrumentar nada más — y confirma que el `TypeError` ocurrió. Corre este mismo flujo con un navegador visible y `POSTHOG_PROJECT_API_KEY` configurado (sección 7) para ver el mismo error como un evento `$exception` en PostHog, con su session replay:
   ```bash
   pytest tests/e2e/test_reportes_de_errores.py --base-url=http://localhost:8000 --headed -v
   ```
