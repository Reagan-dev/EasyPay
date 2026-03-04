from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Withdrawal
from ledger.models import LedgerAccount, LedgerEntry
from wallets.models import Wallet
from notifications.models import Notification

@receiver(post_save, sender=Withdrawal)
def handle_withdrawal_updates(sender, instance, created, **kwargs):
    """
    Handles Ledger entries on Success and Refunds on Failure.
    Note: Wallet deduction now happens in the View to prevent double-spending.
    """
    
    # --- CASE 1: SUCCESSFUL WITHDRAWAL ---
    if instance.status == "SUCCESS" and not instance.ledger_entry:
        try:
            with transaction.atomic():
                user = instance.user
                
                # 1. Improved Wallet/Ledger Mapping (Matching your logic)
                if hasattr(user, 'business'):
                    account_type = "BUSINESS_PAYOUT"
                elif hasattr(user, 'student_profile'):
                    account_type = "STUDENT_POCKET"
                else:
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
                # This balances the books. Debit User (Reduction), Credit System/Mpesa
                ledger_move = LedgerEntry.create_transaction(
                    debit_acc=user_ledger,
                    credit_acc=system_ledger,
                    amount=instance.amount,
                    ref=f"WDL-{instance.id}",
                    desc=f"M-Pesa Withdrawal Success: {instance.external_reference}"
                )

                # 4. Finalize - Use update() to avoid recursion
                Withdrawal.objects.filter(id=instance.id).update(ledger_entry=ledger_move)

                # 5. Notify the User
                Notification.objects.create(
                    user=user,
                    title="Withdrawal Successful",
                    body=f"KES {instance.amount} has been sent to your M-Pesa. Ref: {instance.external_reference}",
                    notification_type="WITHDRAWAL_SUCCESS"
                )
        except Exception as e:
            print(f"CRITICAL: Withdrawal Success Signal Error: {e}")

    # --- CASE 2: FAILED WITHDRAWAL (REFUND LOGIC) ---
    elif instance.status == "FAILED":
        try:
            with transaction.atomic():
                user = instance.user
                
                # RE-CALCULATE the wallet type since it's not in the DB
                if hasattr(user, 'business'):
                    w_type = "SETTLEMENT"
                elif hasattr(user, 'student_profile'):
                    w_type = "POCKET"
                else:
                    w_type = "PERSONAL"

                wallet = Wallet.objects.select_for_update().get(
                    owner_id=user.id, 
                    type=w_type
                )
                
                wallet.balance += instance.amount
                wallet.save()
                
                # Notify user
                Notification.objects.create(
                    user=user,
                    title="Withdrawal Failed",
                    body=f"Your withdrawal of KES {instance.amount} failed. Funds returned to {w_type} wallet.",
                    notification_type="WITHDRAWAL_FAILED"
                )
        except Exception as e:
            print(f"Refund Error: {e}")