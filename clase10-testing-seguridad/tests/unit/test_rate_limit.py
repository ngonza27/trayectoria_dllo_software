"""
Slide 17 — Rate Limiting logic tested in isolation, with a fake clock so the
test is fast and deterministic (no real time.sleep calls, per slide 6's
"rápidas, deterministas" rule for unit tests).
"""

from app.security.rate_limit import FixedWindowRateLimiter


class FakeClock:
    def __init__(self, start: float = 0.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_allows_requests_up_to_the_limit():
    # Arrange
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=60, clock=clock)

    # Act
    results = [limiter.check("client-a")[0] for _ in range(3)]

    # Assert
    assert results == [True, True, True]


def test_blocks_the_request_that_exceeds_the_limit():
    # Arrange
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=2, window_seconds=60, clock=clock)
    limiter.check("client-a")
    limiter.check("client-a")

    # Act
    allowed, retry_after = limiter.check("client-a")

    # Assert
    assert allowed is False
    assert retry_after > 0


def test_resets_after_the_window_elapses():
    # Arrange
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=1, window_seconds=10, clock=clock)
    limiter.check("client-a")
    assert limiter.check("client-a")[0] is False  # second request in the same window is blocked

    # Act
    clock.advance(11)
    allowed, _ = limiter.check("client-a")

    # Assert
    assert allowed is True


def test_counters_are_independent_per_key():
    # Arrange
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=1, window_seconds=60, clock=clock)

    # Act
    limiter.check("client-a")
    allowed_for_b, _ = limiter.check("client-b")

    # Assert — client-b's own budget is untouched by client-a's requests
    assert allowed_for_b is True
