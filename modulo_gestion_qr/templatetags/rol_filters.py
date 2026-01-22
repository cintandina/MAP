from django import template

register = template.Library()

@register.filter
def has_rol(user, rol_name):
    """
    Filtro personalizado para verificar si un usuario tiene un rol específico.
    Uso en la plantilla: {% if request.user|has_rol:"nombre_del_rol" %}
    """
    if user.is_authenticated:  # Asegura que el usuario esté autenticado
        return user.roles.filter(nombre=rol_name).exists()
    return False
