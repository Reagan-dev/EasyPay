# apps/wallets/models.py or apps/deposits/models.py

import uuid

from django.db import models

from django.conf import settings



class Deposit(models.Model):

    STATUS_CHOICES = [

        ('PENDING', 'Pending'),

        ('SUCCESS', 'Success'),

        ('FAILED', 'Failed'),

        ('REVERSED', 'Reversed'),

    ]
    TARGET_CHOICES = [
        ("MEAL", "Meal Wallet"),
        ("POCKET", "Pocket Wallet"),
        ("PERSONAL", "Personal Wallet"), # For Guardians
    ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    target_wallet = models.CharField(max_length=20, choices=TARGET_CHOICES, default="PERSONAL") # Default to personal for guardians and business, students can choose meal or pocket
   

    # Financials

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Gross amount deposited

    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Any platform processing fees

   

    # Tracking

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

   

    # Linking to M-Pesa

    # This links the deposit to the specific M-Pesa callback record

    mpesa_reference = models.OneToOneField(

        'mpesa.MpesaTransaction',

        on_delete=models.SET_NULL,

        null=True,

        blank=True

    )



    # Link to Ledger (Source of Truth)

    ledger_entry = models.OneToOneField(

        'ledger.LedgerEntry',

        on_delete=models.PROTECT,

        null=True,

        blank=True

    )



    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):

        return f"Deposit {self.amount} KES by {self.user.phone} - {self.status}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),  # In newer Django, 'check' was renamed/aliased to 'condition' in some contexts, or requires keyword 'check'
                name="deposit_amount_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(fee__gte=0),
                name="deposit_fee_non_negative",
            ),
        ]

    def save(self, *args, **kwargs):
        """
        Enforce allowed status transitions to prevent regressions.
        PENDING -> {PENDING, SUCCESS, FAILED, REVERSED}
        SUCCESS -> {SUCCESS, REVERSED}
        FAILED  -> {FAILED}
        REVERSED -> {REVERSED}
        """
        if self.pk:
            previous = Deposit.objects.get(pk=self.pk)
            prev_status = previous.status
            new_status = self.status
            allowed = {
                "PENDING": {"PENDING", "SUCCESS", "FAILED", "REVERSED"},
                "SUCCESS": {"SUCCESS", "REVERSED"},
                "FAILED": {"FAILED"},
                "REVERSED": {"REVERSED"},
            }
            if new_status not in allowed.get(prev_status, {prev_status}):
                raise ValueError(
                    f"Invalid Deposit status transition {prev_status} -> {new_status}"
                )
        return super().save(*args, **kwargs)