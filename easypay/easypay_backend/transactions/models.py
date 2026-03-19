import uuid
from django.db import models
from merchants.models import Business
from payments.models import PaymentIntent
from ledger.models import LedgerEntry
from decimal import Decimal
from accounts.models import User

class Transaction(models.Model):
    PAYER_CHOICES = [("STUDENT","STUDENT"), ("CUSTOMER","CUSTOMER")]
    WALLET_CHOICES = [("MEAL","MEAL"), ("POCKET","POCKET"), ("PERSONAL","PERSONAL"), ("SETTLEMENT","SETTLEMENT"), ("REVENUE","REVENUE")]
    STATUS_CHOICES = [("SUCCESS","SUCCESS"), ("FAILED","FAILED"), ("PENDING","PENDING")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


    # Generic Payer Tracking
    payer_type = models.CharField(max_length=20, choices=PAYER_CHOICES)
    payer_id = models.UUIDField() # ID of either the Student or Customer

    # Financial Details
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    wallet_type = models.CharField(max_length=20, choices=WALLET_CHOICES)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)           # The total amount of the transaction
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("3.00")) # Our cut (KES 3)
    
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

    class Meta:
        # A PaymentIntent should only ever produce a single Transaction.
        constraints = [
            models.UniqueConstraint(
                fields=["payment_intent"],
                name="uniq_transaction_per_payment_intent",
            ),
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="transaction_amount_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(platform_fee__gte=0),
                name="transaction_fee_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(platform_fee__lte=models.F("amount")),
                name="transaction_fee_not_exceed_amount",
            ),
        ]

    def save(self, *args, **kwargs):
        """
        Enforce allowed status transitions to prevent regressions.
        PENDING -> {PENDING, SUCCESS, FAILED}
        SUCCESS -> {SUCCESS}
        FAILED  -> {FAILED}
        """
        if not self._state.adding:
            previous = Transaction.objects.filter(pk=self.pk).only("status").first()
            if previous:
                prev_status = previous.status
                new_status = self.status
                allowed = {
                    "PENDING": {"PENDING", "SUCCESS", "FAILED"},
                    "SUCCESS": {"SUCCESS"},
                    "FAILED": {"FAILED"},
                }
                if new_status not in allowed.get(prev_status, {prev_status}):
                    raise ValueError(
                        f"Invalid Transaction status transition {prev_status} -> {new_status}"
                    )
        return super().save(*args, **kwargs)

    @property
    def merchant_payout(self):
        """The actual amount the merchant receives after the fee."""
        return self.amount - self.platform_fee

    def __str__(self):
        return f"TXN-{self.id} | {self.payer_type} -> {self.business.name}"
