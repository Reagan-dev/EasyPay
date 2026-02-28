from django.apps import AppConfig


class WithdrawalConfig(AppConfig):
    name = 'withdrawal'
    def ready(self):
        import withdrawal.signals  # Import signals to ensure they are registered when the app is ready
