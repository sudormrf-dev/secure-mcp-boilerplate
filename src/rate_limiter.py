"""Token bucket rate limiter."""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class TokenBucket:
    """A single token bucket that tracks available tokens and refills over time."""

    capacity: float
    refill_rate: float  # tokens per second
    _tokens: float = field(init=False)
    _last_refill: float = field(init=False)

    def __post_init__(self) -> None:
        self._tokens = self.capacity
        self._last_refill = time.monotonic()

    def consume(self, tokens: float = 1.0) -> bool:
        """Try to consume tokens. Return True if available, False if rate-limited."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
        self._last_refill = now
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False


class RateLimiter:
    """Per-client rate limiter.

    Includes a maximum number of tracked clients to prevent memory exhaustion
    from an attacker sending requests with many unique client IDs.
    """

    MAX_CLIENTS: int = 10_000

    def __init__(self, capacity: float = 10.0, refill_rate: float = 1.0) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets: dict[str, TokenBucket] = {}

    def is_allowed(self, client_id: str) -> bool:
        """Check whether a request from *client_id* is allowed."""
        if client_id not in self._buckets:
            if len(self._buckets) >= self.MAX_CLIENTS:
                # Evict the oldest entry to cap memory usage.
                oldest_key = next(iter(self._buckets))
                del self._buckets[oldest_key]
            self._buckets[client_id] = TokenBucket(self.capacity, self.refill_rate)
        return self._buckets[client_id].consume()
