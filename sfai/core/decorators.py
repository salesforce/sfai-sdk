from functools import wraps
from sfai.context.manager import ContextManager

ctx_mgr = ContextManager()


def with_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "context" not in kwargs:
            kwargs["context"] = ctx_mgr.read_context()
        return func(*args, **kwargs)

    return wrapper
