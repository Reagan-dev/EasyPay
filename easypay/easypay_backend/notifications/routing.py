from django.urls import re_path
from .consumers import PaymentNotificationConsumer

websocket_urlpatterns = [
    # The phone will connect to: ws://domain.com/ws/notifications/
    re_path(r'ws/notifications/$', PaymentNotificationConsumer.as_asgi()),
]