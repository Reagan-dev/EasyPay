import uuid
from django.db import models
from merchants.models import Business
from payments.models import PaymentIntent
from ledger.models import LedgerEntry

class Transaction(models.Model):
    PAYER_CHOICES = [("STUDENT","STUDENT"), ("CUSTOMER","CUSTOMER")]
    WALLET_CHOICES = [("MEAL","MEAL"), ("POCKET","POCKET"), ("PERSONAL","PERSONAL"), ("SETTLEMENT","SETTLEMENT"), ("REVENUE","REVENUE")]
    STATUS_CHOICES = [("SUCCESS","SUCCESS"), ("FAILED","FAILED"), ("PENDING","PENDING")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Generic Payer Tracking
    payer_type = models.CharField(max_length=20, choices=PAYER_CHOICES)
    payer_id = models.UUIDField() # ID of either the Student or Customer

    # Financial Details
    business = models.ForeignKey(Business, on_delete=models.PROTECT)
    wallet_type = models.CharField(max_length=20, choices=WALLET_CHOICES)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)           # The total amount of the transaction
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, default=3.00) # Our cut (KES 3)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    
    # Links to other apps
    payment_intent = models.ForeignKey(
        PaymentIntent, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="transactions"
    )
    # The OneToOne link ensures every transaction is backed by a ledger move
    ledger_entry = models.OneToOneField(
        LedgerEntry, 
        on_delete=models.PROTECT, 
        null=True, # Allow null until the ledger entry is actually created
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def merchant_payout(self):
        """The actual amount the merchant receives after the fee."""
        return self.amount - self.platform_fee

    def __str__(self):
        return f"TXN-{self.id} | {self.payer_type} -> {self.business.name}"
