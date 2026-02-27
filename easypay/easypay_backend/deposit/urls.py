from django.urls import path
from .views import DepositInitiateView, DepositHistoryView

app_name = 'deposit'

urlpatterns = [
    # Endpoint to trigger the M-Pesa STK Push
    path('initiate/', DepositInitiateView.as_view(), name='initiate-stk'),
    
    # Endpoint to see past deposits (The "History" tab in the app)
    path('history/', DepositHistoryView.as_view(), name='deposit-history'),
]