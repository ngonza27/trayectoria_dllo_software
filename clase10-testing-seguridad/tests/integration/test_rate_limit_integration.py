"""
Slide 17 — end-to-end through real HTTP (unlike tests/unit/test_rate_limit.py,
which tests the limiter's own logic in isolation). This builds its own tiny
app with a deliberately low limit, instead of reusing the shared `app` from
conftest.py, so it never interferes with — or gets interfered by — the
auth-flow tests that also call /auth/login.
"""

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
    # Arrange
    client = TestClient(_make_app(max_requests=2))

    # Act
    first = client.get("/ping")
    second = client.get("/ping")
    third = client.get("/ping")

    # Assert
    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert "Retry-After" in third.headers


def test_each_client_ip_has_its_own_budget():
    # Arrange — the middleware reads X-Forwarded-For to find the real client
    # behind a proxy/load balancer (see RateLimitMiddleware._client_ip)
    client = TestClient(_make_app(max_requests=1))

    # Act
    first_ip_first_call = client.get("/ping", headers={"X-Forwarded-For": "10.0.0.1"})
    first_ip_second_call = client.get("/ping", headers={"X-Forwarded-For": "10.0.0.1"})
    second_ip_first_call = client.get("/ping", headers={"X-Forwarded-For": "10.0.0.2"})

    # Assert
    assert first_ip_first_call.status_code == 200
    assert first_ip_second_call.status_code == 429  # 10.0.0.1 already used its one request
    assert second_ip_first_call.status_code == 200  # 10.0.0.2's budget is untouched
