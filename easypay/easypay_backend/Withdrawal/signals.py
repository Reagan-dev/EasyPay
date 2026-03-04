from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Withdrawal
from ledger.models import LedgerAccount, LedgerEntry, SYSTEM_PLATFORM_ID
from wallets.models import Wallet
from notifications.models import Notification
from finance.mappings import (
    get_withdrawal_wallet_type_for_user,
    get_ledger_account_type_for_wallet,
)

@receiver(post_save, sender=Withdrawal)
def handle_withdrawal_updates(sender, instance, created, **kwargs):
    """
    Handles Ledger entries on Success and Refunds on Failure.
    Note: Wallet deduction now happens in the View to prevent double-spending.
    """
    
    # Determine previous status for transition-aware handling
    previous_status = None
    if not created and instance.pk:
        try:
            previous_status = sender.objects.only("status").get(pk=instance.pk).status
        except sender.DoesNotExist:
            previous_status = None

    # --- CASE 1: SUCCESSFUL WITHDRAWAL ---
    # Only act on a real transition into SUCCESS
    if (
        instance.status == "SUCCESS"
        and previous_status != "SUCCESS"
        and not instance.ledger_entry
    ):
        try:
            with transaction.atomic():
                user = instance.user

                # 1. Ledger account mapping derived from the central wallet→ledger mapping
                w_type = get_withdrawal_wallet_type_for_user(user)
                account_type = get_ledger_account_type_for_wallet(w_type)

                # 2. Get Ledger Accounts
                user_ledger = LedgerAccount.objects.get(
                    owner_id=user.id, account_type=account_type
                )

                system_id = SYSTEM_PLATFORM_ID
                system_ledger, _ = LedgerAccount.objects.get_or_create(
                    owner_id=system_id,
                    account_type="PLATFORM_REVENUE",
                    defaults={"balance": 0},
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
    # Only act on a real transition into FAILED, and only once
    elif instance.status == "FAILED" and previous_status != "FAILED":
        try:
            with transaction.atomic():
                user = instance.user

                # RE-CALCULATE the wallet type since it's not in the DB
                w_type = get_withdrawal_wallet_type_for_user(user)

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