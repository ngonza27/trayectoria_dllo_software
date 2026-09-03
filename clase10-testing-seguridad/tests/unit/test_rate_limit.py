from app.security.rate_limit import FixedWindowRateLimiter


class FakeClock:
    def __init__(self, start: float = 0.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_allows_requests_up_to_the_limit():
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=60, clock=clock)

    results = [limiter.check("client-a")[0] for _ in range(3)]

    assert results == [True, True, True]


def test_blocks_the_request_that_exceeds_the_limit():
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=2, window_seconds=60, clock=clock)
    limiter.check("client-a")
    limiter.check("client-a")

    allowed, retry_after = limiter.check("client-a")

    assert allowed is False
    assert retry_after > 0


def test_resets_after_the_window_elapses():
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=1, window_seconds=10, clock=clock)
    limiter.check("client-a")
    assert limiter.check("client-a")[0] is False

    clock.advance(11)
    allowed, _ = limiter.check("client-a")

    assert allowed is True


def test_counters_are_independent_per_key():
    clock = FakeClock()
    limiter = FixedWindowRateLimiter(max_requests=1, window_seconds=60, clock=clock)

    limiter.check("client-a")
    allowed_for_b, _ = limiter.check("client-b")

    assert allowed_for_b is True
