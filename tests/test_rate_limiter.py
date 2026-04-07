"""Tests for token bucket rate limiter."""
from src.rate_limiter import RateLimiter, TokenBucket


def test_token_bucket_allows_within_capacity() -> None:
    bucket = TokenBucket(capacity=5.0, refill_rate=1.0)
    for _ in range(5):
        assert bucket.consume() is True


def test_token_bucket_blocks_when_empty() -> None:
    bucket = TokenBucket(capacity=2.0, refill_rate=0.0)  # no refill
    bucket.consume()
    bucket.consume()
    assert bucket.consume() is False


def test_rate_limiter_per_client() -> None:
    rl = RateLimiter(capacity=3.0, refill_rate=0.0)
    assert rl.is_allowed("client_a") is True
    assert rl.is_allowed("client_a") is True
    assert rl.is_allowed("client_a") is True
    assert rl.is_allowed("client_a") is False
    # Different client has its own bucket
    assert rl.is_allowed("client_b") is True


def test_rate_limiter_independence() -> None:
    rl = RateLimiter(capacity=1.0, refill_rate=0.0)
    assert rl.is_allowed("x") is True
    assert rl.is_allowed("x") is False
    assert rl.is_allowed("y") is True


def test_rate_limiter_max_clients_eviction() -> None:
    """Verify that the rate limiter evicts old entries when MAX_CLIENTS is reached."""
    rl = RateLimiter(capacity=1.0, refill_rate=0.0)
    rl.MAX_CLIENTS = 3  # lower for testing
    for i in range(4):
        rl.is_allowed(f"client_{i}")
    # Only 3 buckets should be tracked (oldest evicted)
    assert len(rl._buckets) == 3
    assert "client_0" not in rl._buckets
