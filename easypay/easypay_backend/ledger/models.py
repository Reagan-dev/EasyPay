import uuid
from django.db import models, transaction

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
        with transaction.atomic():
            # Create the entry
            entry = cls.objects.create(
                debit_account=debit_acc,
                credit_account=credit_acc,
                amount=amount,
                reference=ref,
                description=desc
            )
            
            # Update balances
            # Debit: Usually decreases asset or increases liability (In our logic: Payer -)
            debit_acc.balance -= amount
            debit_acc.save()
            
            # Credit: Usually increases asset (In our logic: Receiver +)
            credit_acc.balance += amount
            credit_acc.save()
            
            return entry