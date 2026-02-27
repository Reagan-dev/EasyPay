from django.urls import path
from .views import (
    NotificationListView, 
    NotificationMarkReadView, 
    NotificationBulkMarkReadView
)

app_name = 'notifications'

urlpatterns = [
    # Get the list of alerts
    path('', NotificationListView.as_view(), name='list'),
    
    # Mark a specific alert as read
    path('<uuid:id>/read/', NotificationMarkReadView.as_view(), name='mark-read'),
    
    # "Mark all as read" button logic
    path('read-all/', NotificationBulkMarkReadView.as_view(), name='mark-all-read'),
]