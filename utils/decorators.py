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


def single_use(f):
    """
    Decorator that ensures that a function can only be called once.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if decorated.__called:
            raise RuntimeError("This function can only be called once.")
        decorated.__called = True
        return f(*args, **kwargs)

    decorated.__called = False
    return decorated
