from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.security.rate_limit import FixedWindowRateLimiter, RateLimitMiddleware


def _make_app(max_requests: int) -> FastAPI:
    app = FastAPI()

    @app.get("/ping")
    def ping():
        return {"ok": True}

    app.add_middleware(
        RateLimitMiddleware,
        limiter=FixedWindowRateLimiter(max_requests=max_requests, window_seconds=60),
        protected_paths={"/ping"},
    )
    return app


def test_returns_429_with_retry_after_once_the_limit_is_exceeded():
    client = TestClient(_make_app(max_requests=2))

    first = client.get("/ping")
    second = client.get("/ping")
    third = client.get("/ping")

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert "Retry-After" in third.headers


def test_each_client_ip_has_its_own_budget():
    client = TestClient(_make_app(max_requests=1))

    first_ip_first_call = client.get("/ping", headers={"X-Forwarded-For": "10.0.0.1"})
    first_ip_second_call = client.get("/ping", headers={"X-Forwarded-For": "10.0.0.1"})
    second_ip_first_call = client.get("/ping", headers={"X-Forwarded-For": "10.0.0.2"})

    assert first_ip_first_call.status_code == 200
    assert first_ip_second_call.status_code == 429
    assert second_ip_first_call.status_code == 200
