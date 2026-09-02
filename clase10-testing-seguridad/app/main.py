from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import admin, auth, reservas
from app.security.rate_limit import FixedWindowRateLimiter, RateLimitMiddleware

app = FastAPI(title="Reservas API — Clase 10: Seguridad y Pruebas (Fresh Fork Restaurant Group)")

# Slide 17 — Rate Limiting: applied at /auth/login, the classic brute-force target.
limiter = FixedWindowRateLimiter(
    max_requests=settings.rate_limit_max_requests,
    window_seconds=settings.rate_limit_window_seconds,
)
app.add_middleware(RateLimitMiddleware, limiter=limiter, protected_paths={"/auth/login"})

app.include_router(auth.router)
app.include_router(reservas.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/public-config")
def public_config():
    """
    Slide 8/11 — PostHog: the frontend (static/analytics.js) fetches this on
    every page load instead of hardcoding a key into static files, so the
    project API key stays sourced from the environment. This key is safe to
    expose to the browser — it's the same key posthog-js always embeds
    client-side; it is NOT the secret personal API key (see app/config.py).
    """
    return {
        "posthog_project_api_key": settings.posthog_project_api_key,
        "posthog_host": settings.posthog_host,
    }


# Minimal static frontend (plain HTML/JS) so Playwright has a real UI to
# drive end-to-end — see tests/e2e/ and static/analytics.js.
# Mounted last so the API routes above are matched first.
static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
