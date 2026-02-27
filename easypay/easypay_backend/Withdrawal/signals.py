from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Withdrawal
from ledger.models import LedgerAccount, LedgerEntry
from wallets.models import Wallet
from notifications.models import Notification

@receiver(post_save, sender=Withdrawal)
def handle_withdrawal_completion(sender, instance, created, **kwargs):
    if instance.status == "SUCCESS" and not instance.ledger_entry:
        try:
            with transaction.atomic():
                # 1. Improved Wallet/Ledger Mapping
                user = instance.user
                if hasattr(user, 'business'):
                    wallet_type = "SETTLEMENT"
                    account_type = "BUSINESS_PAYOUT"
                elif hasattr(user, 'student_profile'): # Assuming student profile relation
                    wallet_type = "POCKET"
                    account_type = "STUDENT_POCKET"
                else:
                    wallet_type = "PERSONAL"
                    account_type = "CUSTOMER_MAIN"

                # 2. Get Ledger Accounts
                user_ledger = LedgerAccount.objects.get(owner_id=user.id, account_type=account_type)
                
                system_id = "00000000-0000-0000-0000-000000000000"
                system_ledger, _ = LedgerAccount.objects.get_or_create(
                    owner_id=system_id,
                    account_type="PLATFORM_REVENUE", 
                    defaults={'balance': 0}
                )

                # 3. Create Ledger Entry
                ledger_move = LedgerEntry.create_transaction(
                    debit_acc=user_ledger,
                    credit_acc=system_ledger,
                    amount=instance.amount,
                    ref=f"WDL-{instance.id}",
                    desc=f"M-Pesa Withdrawal: {instance.external_reference}"
                )

                # 4. Update Wallet
                wallet = Wallet.objects.get(owner_id=user.id, type=wallet_type)
                wallet.balance -= instance.amount
                wallet.save()

                # 5. Finalize
                instance.ledger_entry = ledger_move
                # Use update() to avoid re-triggering the signal recursively
                Withdrawal.objects.filter(id=instance.id).update(ledger_entry=ledger_move)

                # 6. Notify
                Notification.objects.create(
                    user=user,
                    title="Withdrawal Successful",
                    body=f"KES {instance.amount} has been sent to your M-Pesa.",
                    notification_type="WITHDRAWAL_SUCCESS"
                )
        except Exception as e:
            print(f"Withdrawal Signal Error: {e}")