import uuid
from django.db import models, transaction, IntegrityError

SYSTEM_PLATFORM_ID = "00000000-0000-0000-0000-000000000000"

class LedgerAccount(models.Model):
    ACCOUNT_TYPES = [
        ("STUDENT_MEAL", "Student Meal Wallet"),
        ("STUDENT_POCKET", "Student Pocket Wallet"),
        ("CUSTOMER_MAIN", "Guardian Primary Wallet"),
        ("BUSINESS_PAYOUT", "Business Settlement Account"),
        ("PLATFORM_REVENUE", "EasyPay Revenue Account"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_id = models.UUIDField() 
    account_type = models.CharField(max_length=30, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00) # Total Sum
    
    class Meta:
        unique_together = ("owner_id", "account_type")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name="ledgeraccount_balance_non_negative",
            ),
        ]

class LedgerEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    debit_account = models.ForeignKey(LedgerAccount, on_delete=models.PROTECT, related_name="debits")
    credit_account = models.ForeignKey(LedgerAccount, on_delete=models.PROTECT, related_name="credits")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    reference = models.CharField(max_length=100, unique=True) # Idempotency Key
    description = models.CharField(max_length=255, blank=True) # e.g., "Lunch at Main Mess"
    status = models.CharField(max_length=20, choices=[("POSTED","POSTED"),("REVERSED","REVERSED")], default="POSTED")
    created_at = models.DateTimeField(auto_now_add=True)

    # The Atomic Transfer
    @classmethod
    def create_transaction(cls, debit_acc, credit_acc, amount, ref, desc=""):
        """
        Ensures that both accounts are updated and the entry is saved
        OR nothing happens at all (Atomicity).
        """
        if amount <= 0:
            raise ValueError("Amount must be positive.")

        with transaction.atomic():
            # Always work with locked, fresh copies of the accounts to avoid lost updates.
            # Lock ordering by primary key to minimise deadlock risk.
            debit_id = debit_acc.pk
            credit_id = credit_acc.pk

            first_id, second_id = sorted([debit_id, credit_id])
            locked_accounts = (
                LedgerAccount.objects.select_for_update()
                .filter(pk__in=[first_id, second_id])
                .in_bulk()
            )

            locked_debit = locked_accounts[debit_id]
            locked_credit = locked_accounts[credit_id]

            # Re-check sufficient balance for the debit side inside the transaction.
            if locked_debit.balance < amount:
                raise ValueError("Insufficient ledger balance for debit.")

            try:
                entry = cls.objects.create(
                    debit_account=locked_debit,
                    credit_account=locked_credit,
                    amount=amount,
                    reference=ref,
                    description=desc,
                )
            except IntegrityError:
                # Duplicate reference => treat as idempotent and return the existing entry.
                existing = cls.objects.get(reference=ref)
                return existing

            # Apply the balance movements on the locked rows.
            locked_debit.balance -= amount
            locked_credit.balance += amount

            # Safety: prevent negative balances from being persisted.
            if locked_debit.balance < 0:
                raise ValueError("Ledger debit would result in negative balance.")

            locked_debit.save(update_fields=["balance"])
            locked_credit.save(update_fields=["balance"])

            return entry

    def save(self, *args, **kwargs):
        """
        Enforce immutability of ledger entries after creation.
        Financial corrections must be done via new reversing entries.
        """
        if self.pk and LedgerEntry.objects.filter(pk=self.pk).exists():
            raise ValueError("LedgerEntry records are immutable once created.")
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="ledgerentry_amount_positive",
            ),
        ]