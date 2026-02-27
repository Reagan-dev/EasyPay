from django.urls import path
from .views import (
    CustomerProfileView, 
    LinkedStudentsView
)

app_name = 'guardians'

urlpatterns = [
    # Guardian's personal profile details
    path('profile/', CustomerProfileView.as_view(), name='profile'),
    
    # Student management: List children or Link a new child via Reg No
    path('students/', LinkedStudentsView.as_view(), name='linked-students'),
]