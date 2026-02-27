from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

@receiver(post_save, sender=Notification)
def broadcast_notification(sender, instance, created, **kwargs):
    """
    Whenever a Notification object is created in the DB, 
    immediately push it to the user's active WebSocket connection.
    """
    if created:
        channel_layer = get_channel_layer()
        group_name = f"user_{instance.user.id}"

        # We extract metadata safely from the JSONField 'data'
        # Defaulting to KES 0 if amount isn't present
        amount = "0"
        if instance.data and isinstance(instance.data, dict):
            amount = str(instance.data.get('amount', '0'))

        # This calls the 'payment_update' method in your PaymentNotificationConsumer
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "payment_update",
                "status": instance.notification_type,
                "amount": amount,
                "message": instance.body,
                "title": instance.title,
                "notification_id": str(instance.id)
            }
        )