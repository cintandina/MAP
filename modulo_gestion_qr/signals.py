# modulo_gestion_qr/signals.py
import logging

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Solicitud

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Solicitud)
def borrar_logo_anterior_si_cambia(sender, instance: Solicitud, **kwargs):
    """
    Si el logo cambia, borra el archivo anterior del storage (S3).
    """
    if not instance.pk:
        return
    try:
        anterior = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    # Si subiste un nuevo archivo (nombre distinto), borra el anterior
    if anterior.logo and instance.logo and anterior.logo.name != instance.logo.name:
        try:
            anterior.logo.storage.delete(anterior.logo.name)
            logger.debug("Logo anterior borrado: %s", anterior.logo.name)
        except Exception as e:
            logger.debug("No se pudo borrar logo anterior: %s", e)

@receiver(post_delete, sender=Solicitud)
def borrar_logo_al_eliminar(sender, instance: Solicitud, **kwargs):
    """
    Si borras la solicitud, borra el archivo del logo del storage.
    """
    if instance.logo:
        try:
            instance.logo.storage.delete(instance.logo.name)
            logger.debug("Logo borrado al eliminar solicitud: %s", instance.logo.name)
        except Exception as e:
            logger.debug("No se pudo borrar logo al eliminar: %s", e)

