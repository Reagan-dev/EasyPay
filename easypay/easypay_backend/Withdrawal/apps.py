from django.apps import AppConfig


class WithdrawalConfig(AppConfig):
    name = 'Withdrawal'
    def ready(self):
        import Withdrawal.signals  # Import signals to ensure they are registered when the app is ready
