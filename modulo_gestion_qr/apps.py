# modulo_gestion_qr/apps.py
from django.apps import AppConfig

class ModuloGestionQrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modulo_gestion_qr'

    def ready(self):
        # registra las signals al iniciar la app
        import modulo_gestion_qr.signals

