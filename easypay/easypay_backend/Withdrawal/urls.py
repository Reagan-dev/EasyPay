from django.urls import path
from .views import WithdrawalRequestView, MpesaWithdrawalCallbackView

app_name = 'Withdrawal'

urlpatterns = [
    # User: "I want to withdraw KES 1000 to my phone"
    path('request/', WithdrawalRequestView.as_view(), name='withdrawal-request'),
    
    # Safaricom: "The B2C transfer was successful/failed"
    # This must be exposed to the internet
    path('callback/', MpesaWithdrawalCallbackView.as_view(), name='b2c-callback'),
]