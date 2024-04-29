import time
from functools import wraps


def ttl(t: int):
    """
    Decorator that caches the result of a function with no arguments for a given time (in seconds).
    """

    def decorator(f):
        f.__last_call = 0
        f.__result = None

        @wraps(f)
        def decorated():
            if int(time.time()) - f.__last_call > t:
                f.__result = f()
                f.__last_call = int(time.time())
            return f.__result

        return decorated

    return decorator
