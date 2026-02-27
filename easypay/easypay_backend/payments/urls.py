from django.urls import path
from .views import CreatePaymentIntentView, PaymentIntentDetailView

app_name = 'payments'

urlpatterns = [
    # Canteen Staff: "I want to charge KES 50.00"
    path('intent/create/', CreatePaymentIntentView.as_view(), name='create-intent'),
    
    # Canteen Staff Phone: "Did the student scan it yet? Is the money in?"
    # The phone will poll this URL or wait for the WebSocket signal
    path('intent/<uuid:pk>/', PaymentIntentDetailView.as_view(), name='intent-detail'),
]