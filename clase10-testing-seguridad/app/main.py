from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import auth_routes, reservas_routes
from app.security.rate_limit import FixedWindowRateLimiter, RateLimitMiddleware

app = FastAPI(title="Reservas API — Clase 10: Seguridad y Pruebas (Fresh Fork Restaurant Group)")

limiter = FixedWindowRateLimiter(
    max_requests=settings.rate_limit_max_requests,
    window_seconds=settings.rate_limit_window_seconds,
)
app.add_middleware(RateLimitMiddleware, limiter=limiter, protected_paths={"/auth/login"})

app.include_router(auth_routes.router)
app.include_router(reservas_routes.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/public-config")
def public_config():
    return {
        "posthog_project_api_key": settings.posthog_project_api_key,
        "posthog_host": settings.posthog_host,
    }


static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
