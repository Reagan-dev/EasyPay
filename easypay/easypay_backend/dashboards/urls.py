from django.urls import path
from .views import (
    StudentDashboardView, 
    MerchantDashboardView, 
    GuardianDashboardView
)

app_name = 'dashboards'

urlpatterns = [
    # Dedicated endpoints for each user experience
    path('student/', StudentDashboardView.as_view(), name='student-home'),
    path('merchant/', MerchantDashboardView.as_view(), name='merchant-home'),
    path('guardian/', GuardianDashboardView.as_view(), name='guardian-home'),
]