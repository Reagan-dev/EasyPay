from django.urls import path
from .views import LedgerAccountSummaryView, LedgerStatementView

app_name = 'ledger'

urlpatterns = [
    # Get a list of all accounts (Meal, Pocket, etc.) and their current balances
    path('accounts/', LedgerAccountSummaryView.as_view(), name='account-summary'),
    
    # Get the transaction history for a specific account type
    path('statement/<str:account_type>/', LedgerStatementView.as_view(), name='account-statement'),
]