from django import template
import re

register = template.Library()

@register.filter
def phone_format(value):
    if not value:
        return ""
    # Elimina caracteres no numéricos y añade prefijo +57 si no está
    cleaned = re.sub(r'\D', '', value)
    return f"+57{cleaned}" if not cleaned.startswith('+') else cleaned