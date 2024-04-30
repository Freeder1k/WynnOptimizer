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
        is_method = False
        method = None
        if len(args) > 0:
            method = getattr(args[0], f.__name__, False)
            if method:
                wrapped = getattr(method, "__wrapped__", False)
                if wrapped and wrapped == f:
                    is_method = True

        if is_method:
            if not getattr(args[0], "__called_methods", False):
                args[0].__called_methods = set()
            if f.__name__ in args[0].__called_methods:
                raise RuntimeError("This method can only be called once.")
            args[0].__called_methods.add(f.__name__)
        else:
            if getattr(f, "__called", False):
                raise RuntimeError("This function can only be called once.")
            f.__setattr__("__called", True)
        return f(*args, **kwargs)

    return decorated
