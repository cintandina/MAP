from django.http import HttpResponseForbidden
from functools import wraps

def role_required(rol_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and (request.user.is_admin() or request.user.has_rol(rol_name)):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permisos para acceder a esta página.")
        return wrapper
    return decorator

