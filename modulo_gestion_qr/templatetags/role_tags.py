from django import template

register = template.Library()

@register.filter
def has_rol(user, rol_name):
    """Comprueba si el usuario tiene un rol específico."""
    if user.is_authenticated:
        return user.has_rol(rol_name)
    return False
