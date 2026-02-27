from django.urls import path
from .views import StudentProfileView, StudentCreateView

app_name = 'students'

urlpatterns = [
    # Used after registration to set the student's reg_no
    path('setup/', StudentCreateView.as_view(), name='student-setup'),
    
    # The main profile endpoint for the student dashboard
    path('me/', StudentProfileView.as_view(), name='student-me'),
]