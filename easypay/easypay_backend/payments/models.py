import uuid
from django.db import models
from django.db.models import Q
from django.utils import timezone
from merchants.models import Business, BusinessTerminal

class PaymentIntent(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "PENDING"),     # Waiting for a scan
        ("MATCHED", "MATCHED"),     # Scanned, verifying funds/identity
        ("COMPLETED", "COMPLETED"), # Money successfully moved in Ledger
        ("EXPIRED", "EXPIRED"),     # Time ran out
        ("CANCELLED", "CANCELLED"), # Merchant or User aborted
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    terminal = models.ForeignKey(BusinessTerminal, on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    # This allows the ledger to know who to debit
    payer_id = models.UUIDField(null=True, blank=True) 
    payer_type = models.CharField(max_length=20, null=True, blank=True, choices=[("STUDENT", "STUDENT"), ("CUSTOMER", "CUSTOMER")])
    
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["terminal"],
                condition=Q(status="PENDING"),
                name="one_pending_intent_per_terminal"
            )
        ]

    #Quick check if intent is still valid
    @property
    def is_active(self):
        return self.status == "PENDING" and self.expires_at > timezone.now()