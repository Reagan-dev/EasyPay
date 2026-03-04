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

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name="mpesatransaction_amount_non_negative",
            ),
        ]

    def save(self, *args, **kwargs):
        """
        Enforce allowed status transitions to prevent regressions.
        PENDING -> {PENDING, SUCCESS, FAILED}
        SUCCESS -> {SUCCESS}
        FAILED  -> {FAILED}
        """
        if self.pk:
            previous = MpesaTransaction.objects.get(pk=self.pk)
            prev_status = previous.status
            new_status = self.status
            allowed = {
                "PENDING": {"PENDING", "SUCCESS", "FAILED"},
                "SUCCESS": {"SUCCESS"},
                "FAILED": {"FAILED"},
            }
            if new_status not in allowed.get(prev_status, {prev_status}):
                raise ValueError(
                    f"Invalid MpesaTransaction status transition {prev_status} -> {new_status}"
                )
        return super().save(*args, **kwargs)