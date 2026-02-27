from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    name = 'transactions'
    def ready(self):
        import transactions.signals  # Import signals to ensure they are registered when the app is ready
