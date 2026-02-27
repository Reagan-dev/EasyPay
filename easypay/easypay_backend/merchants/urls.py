from django.urls import path
from .views import BusinessProfileView, BusinessTerminalListView

app_name = 'merchants'

urlpatterns = [
    # Main business profile (GET/PATCH)
    path('profile/', BusinessProfileView.as_view(), name='business-profile'),
    
    # Terminal management (List/Register new devices)
    path('terminals/', BusinessTerminalListView.as_view(), name='terminal-list'),
]