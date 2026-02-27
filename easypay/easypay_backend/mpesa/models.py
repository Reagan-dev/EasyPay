import uuid
from django.db import models

class MpesaTransaction(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "PENDING"),
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Safaricom Identifiers (Crucial for tracking STK Push)
    merchant_request_id = models.CharField(max_length=100, db_index=True, null=True)
    checkout_request_id = models.CharField(max_length=100, db_index=True, null=True)
    
    # The actual M-Pesa receipt code (e.g., RBA123456)
    external_txn_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    phone = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    
    # Store the full JSON from Safaricom for audit trails
    raw_payload = models.JSONField(null=True, blank=True)
    
    # Optional: Link to the person who initiated it (if known)
    user_id = models.UUIDField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mpesa {self.external_txn_id or self.checkout_request_id} - {self.status}"