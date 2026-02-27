import uuid
from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('PAYMENT_SENT', 'Payment Sent'),
        ('TOPUP_SUCCESS', 'Top-up Successful'),
        ('LOW_BALANCE', 'Low Balance Alert'),
        ('SYSTEM', 'System Update'),
        ('WITHDRAWAL_PENDING', 'Withdrawal Initiated'),
        ('WITHDRAWAL_SUCCESS', 'Withdrawal Successful'),
        ('WITHDRAWAL_FAILED', 'Withdrawal Failed'),
        ('DEPOSIT_PENDING', 'Deposit Initiated'),
        ('DEPOSIT_SUCCESS', 'Deposit Successful'),
        ('DEPOSIT_FAILED', 'Deposit Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Link to the User model we created in the users app
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="notifications"
    )
    
    title = models.CharField(max_length=255)
    body = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Read/Unread status
    is_read = models.BooleanField(default=False)
    
    # Metadata
    data = models.JSONField(null=True, blank=True) # To store txn_id or other IDs
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Newest notifications first

    def __str__(self):
        return f"{self.notification_type} for {self.user.phone}"