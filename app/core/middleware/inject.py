from functools import wraps

from dependency_injector.wiring import inject as di_inject, _fetch_reference_injections

from app.services.base import BaseService


def inject(func):
    if _fetch_reference_injections(func)[0]:
        injected_func = di_inject(func)
    else:
        injected_func = func

    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await injected_func(*args, **kwargs)
        injected_services = [
            arg for arg in kwargs.values() if isinstance(arg, BaseService)
        ]
        if injected_services:
            try:
                await injected_services[-1].close_scope_session()
            except Exception:
                pass
        return result

    return wrapper
