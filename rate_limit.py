"""Simple in-memory sliding-window rate limiter, one window per user."""
import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict


class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: float,
                 clock: Callable[[], float] = time.monotonic):
        self.max_calls = max_calls
        self.window = window_seconds
        self._clock = clock
        self._calls: Dict[int, Deque[float]] = defaultdict(deque)

    def allow(self, user_id: int) -> bool:
        """Record a call and return True if the user is under the limit."""
        now = self._clock()
        calls = self._calls[user_id]
        while calls and now - calls[0] >= self.window:
            calls.popleft()
        if len(calls) >= self.max_calls:
            return False
        calls.append(now)
        return True
