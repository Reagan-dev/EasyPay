from django.urls import path
from .views import WalletListView, WalletDetailView

app_name = 'wallets'

urlpatterns = [
    # Dashboard: "Show me all my balances"
    path('', WalletListView.as_view(), name='wallet-list'),
    
    # Specific: "How much is exactly in my MEAL wallet?"
    # Example: /api/wallets/MEAL/
    path('<str:type>/', WalletDetailView.as_view(), name='wallet-detail'),
]