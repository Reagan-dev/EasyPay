# apps/withdrawals/models.py
import uuid
from django.db import models
from django.conf import settings

class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    # Amount requested
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Fees for withdrawal
    
    # Destination details
    phone_number = models.CharField(max_length=20) # Usually the user's M-Pesa number
    
    # Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    external_reference = models.CharField(max_length=100, unique=True, null=True, blank=True) # M-Pesa B2C ID
    
    # Link to the Ledger (Very Important!)
    ledger_entry = models.OneToOneField(
        'ledger.LedgerEntry', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"withdrawal {self.amount} KES - {self.status}"