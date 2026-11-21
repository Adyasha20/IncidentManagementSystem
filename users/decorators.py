from functools import wraps
from django.http import HttpResponseForbidden


def role_required(required_role):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if request.user.role != required_role:
                return HttpResponseForbidden(
                    "<h2>403 - Access Denied</h2><p>You are not authorized to view this page.</p>"
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator