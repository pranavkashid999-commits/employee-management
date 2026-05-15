from flask import session
from functools import wraps
from Utils.responce import ERROR_RESPONCE


def role_request(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            role = session.get("role")

            if not role:
                return ERROR_RESPONCE(
                    "unauthorized login please",
                    401
                )

            if role not in allowed_roles:
                return ERROR_RESPONCE(
                    "access denied",
                    403
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator