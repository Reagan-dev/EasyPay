from django.db import models
import uuid

# wallet model to store wallet information for customers and studentsin my easypay project innovation.
class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who owns this wallet?
    owner_type = models.CharField(
        max_length=20,
        choices=[
            ('STUDENT', 'STUDENT'),
            ('CUSTOMER', 'CUSTOMER'),
            ('BUSINESS', 'BUSINESS'),
            ('PLATFORM', 'PLATFORM'), # For your transaction fees/revenue
        ]
    )
    owner_id = models.UUIDField()

    # What is this money for?
    type = models.CharField(
        max_length=20,
        choices=[
            ("MEAL", "MEAL"),         # Restricted student funds
            ("POCKET", "POCKET"),     # Flexible student funds
            ("PERSONAL", "PERSONAL"), # Customer's personal wallet
            ("SETTLEMENT", "SETTLEMENT"), # Merchant funds waiting for withdrawal
            ("REVENUE", "REVENUE"),   # EasyPay's profit
        ]
    )
    
    # Store balance in decimals (e.g., KES 10.00)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    is_withdrawable = models.BooleanField(default=False)  # For settlement wallets, this might be False until funds are cleared

    class Meta:
        unique_together = ("owner_type", "owner_id", "type")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name="wallet_balance_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.owner_type} - {self.type} ({self.balance})"