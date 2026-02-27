from django.urls import path
from .views import ProcessSaleView, MerchantActivityView

app_name = 'transactions'

urlpatterns = [
    # The final handshake: QR Scanned + Terminal Intent matched
    path('process-sale/', ProcessSaleView.as_view(), name='process-sale'),
    
    # Merchant's history of all successful sales/payouts
    path('history/', MerchantActivityView.as_view(), name='merchant-history'),
]