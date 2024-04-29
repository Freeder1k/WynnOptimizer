import time

import requests

from utils.rateLimit import RateLimit
from utils.type.jsonTypes import JsonType

_rate_limit = RateLimit(180, 1)
_rl_reset = 0
_last_req_time = 0


def get(url: str, **params: str) -> JsonType:
    """
    Send a GET request to the wynncraft API V3. This has a ratelimit of 300 requests per minute.
    :param url: The url of the request. Must start with '/'.
    :param retry: Whether to retry the request on "internal server error (500)".
    :param params: Additional request parameters.
    :return: the response in json format.
    """
    with _rate_limit:
        resp = requests.get(f"https://api.wynncraft.com/v3{url}", params=params, timeout=5)
        resp.raise_for_status()
        global _rl_reset, _last_req_time
        _last_req_time = time.time()
        _rl_reset = resp.headers.get("ratelimit-reset")
        _rl_reset = int(_rl_reset) if _rl_reset else 0
        remaining = resp.headers.get("x-ratelimit-remaining-minute")
        remaining = int(remaining) if remaining else 0
        if remaining == 0:
            _rate_limit._set_full()

        return resp.json()


def calculate_remaining_requests():
    return _rate_limit.calculate_remaining_calls()


def ratelimit_reset_time():
    return max(_rl_reset + _last_req_time - time.time(), 0)
