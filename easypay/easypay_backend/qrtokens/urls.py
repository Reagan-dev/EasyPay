from django.urls import path
from .views import GenerateQRTokenView, ValidateQRTokenView

app_name = 'qrtokens'

urlpatterns = [
    # Students/Guardians: "Generate my QR code for this lunch"
    path('generate/', GenerateQRTokenView.as_view(), name='generate-qr'),
    
    # Merchants: "Scan this string and tell me if it's valid"
    # Example: /api/qr/validate/xyz_random_string/
    path('validate/<str:token_value>/', ValidateQRTokenView.as_view(), name='validate-qr'),
]