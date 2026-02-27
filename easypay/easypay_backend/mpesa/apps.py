from django.apps import AppConfig


class MpesaConfig(AppConfig):
    name = 'mpesa'
    def ready(self):
        import mpesa.signals  # Import signals to ensure they are registered when the app is ready
