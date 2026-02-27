from django.urls import path
from .views import MpesaCallbackView

app_name = 'mpesa'

urlpatterns = [
    # Safaricom hits this URL after the user enters their PIN
    # This must match the 'CallBackURL' sent in the STK push request
    path('callback/', MpesaCallbackView.as_view(), name='stk-callback'),
]