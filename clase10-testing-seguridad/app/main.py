from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import accounts, auth
from app.security.rate_limit import FixedWindowRateLimiter, RateLimitMiddleware

app = FastAPI(title="Cuentas API — Clase 10: Seguridad y Pruebas")

# Slide 17 — Rate Limiting: applied at /auth/login, the classic brute-force target.
limiter = FixedWindowRateLimiter(
    max_requests=settings.rate_limit_max_requests,
    window_seconds=settings.rate_limit_window_seconds,
)
app.add_middleware(RateLimitMiddleware, limiter=limiter, protected_paths={"/auth/login"})

app.include_router(auth.router)
app.include_router(accounts.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Minimal static frontend (plain HTML/JS) so Playwright has a real UI to
# drive end-to-end — see tests/e2e/test_login_flow.py and static/README.md.
# Mounted last so the API routes above are matched first.
static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
