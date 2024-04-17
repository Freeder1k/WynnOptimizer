import collections
import time
from http import HTTPStatus
from threading import Lock

from aiohttp import ClientResponseError


class RateLimitException(Exception):
    pass


class RateLimit:
    def __init__(self, max_calls: int, period: int):
        """
        A ratelimit checker. Use with 'with RateLimit:'. If amount requests in the specified time were exceeded throws
        RateLimitException.

        :param max_calls: The amount of requests allowed
        :param period: The time period in minutes of the ratelimit
        """
        self._max_calls = max_calls
        self._period = period
        self._calls = collections.deque(maxlen=max_calls)
        self._lock = Lock()

    def __enter__(self):
        """
        :raises RateLimitException: If the rate limit was exceeded.
         Also catches NonSuccessExceptions and checks for TOO_MANY_REQUESTS code and sets the rate limit to full if so.
        """
        with self._lock:
            if self.calculate_remaining_calls() <= 0:
                raise RateLimitException(f"Rate limit of {self._max_calls} requests per {self._period}min reached!")

            curr_time = time.time()
            self._calls.append(curr_time)

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._lock:
            if exc_type is ClientResponseError and exc_val.status == HTTPStatus.TOO_MANY_REQUESTS:
                usage = self.calculate_usage()
                self._set_full()
                raise RateLimitException(
                    f"Rate limited by server! (Request amount: {usage}/{self._max_calls} per {self._period}min)")

    def _clear_expired_calls(self):
        curr_time = time.time()
        while len(self._calls) > 0 and curr_time - self._calls[0] >= self._period * 60:
            self._calls.popleft()

    def _set_full(self):
        curr_time = time.time()
        self._calls.extend([curr_time] * self.calculate_remaining_calls())

    def calculate_usage(self) -> int:
        """
        Calculates the amount of requests made in the current period. This also clears expired calls.
        """
        self._clear_expired_calls()
        return len(self._calls)

    def calculate_remaining_calls(self) -> int:
        """
        Calculates the amount of requests left in the current period. This also clears expired calls.
        """
        return self.get_max_calls() - self.calculate_usage()

    def get_max_calls(self) -> int:
        """
        :return: The maximum amount of requests allowed
        """
        return self._max_calls

    def get_period(self) -> int:
        """
        :return: The period in minutes
        """
        return self._period

    def get_time_until_next_free(self) -> int:
        """
        :return: The time in seconds until the next free request
        """
        if len(self._calls) == 0:
            return 0
        return max(self._period * 60 + self._calls[0] - time.time(), 0)
