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
    Uses notification existence as a safety guard to prevent double-processing.
    """
    # We only care about updates to existing withdrawals (transitions)
    if created:
        return

    # --- CASE 1: SUCCESSFUL WITHDRAWAL ---
    # We check if a ledger_entry exists to ensure we don't double-book the ledger
    if instance.status == "SUCCESS" and not instance.ledger_entry:
        try:
            with transaction.atomic():
                user = instance.user
                w_type = get_withdrawal_wallet_type_for_user(user)
                account_type = get_ledger_account_type_for_wallet(w_type)

                # 1. Get and Lock Ledger Accounts
                user_ledger = LedgerAccount.objects.select_for_update().get(
                    owner_id=user.id, account_type=account_type
                )

                system_ledger, _ = LedgerAccount.objects.select_for_update().get_or_create(
                    owner_id=SYSTEM_PLATFORM_ID,
                    account_type="PLATFORM_REVENUE",
                    defaults={"balance": 0},
                )

                # 2. Record the Ledger Entry (Debit User, Credit System)
                ledger_move = LedgerEntry.create_transaction(
                    debit_acc=user_ledger,
                    credit_acc=system_ledger,
                    amount=instance.amount,
                    ref=f"WDL-{instance.id}",
                    desc=f"M-Pesa Withdrawal Success: {instance.external_reference}"
                )

                # 3. Finalize Withdrawal record using update() to prevent signal recursion
                Withdrawal.objects.filter(id=instance.id).update(ledger_entry=ledger_move)

                # 4. Notify the User
                Notification.objects.create(
                    user=user,
                    title="Withdrawal Successful",
                    body=f"KES {instance.amount} sent to M-Pesa. Ref: {instance.external_reference}",
                    notification_type="WITHDRAWAL_SUCCESS"
                )
        except Exception as e:
            print(f"CRITICAL: Withdrawal Success Ledger Error: {e}")

    # --- CASE 2: FAILED WITHDRAWAL (REFUND LOGIC) ---
    elif instance.status == "FAILED":
        try:
            with transaction.atomic():
                user = instance.user
                w_type = get_withdrawal_wallet_type_for_user(user)

                # IDEMPOTENCY GUARD: Check if we have already issued a refund notification 
                # for this specific withdrawal ID. This prevents double-refunds.
                refund_exists = Notification.objects.filter(
                    user=user,
                    notification_type="WITHDRAWAL_FAILED",
                    body__contains=str(instance.id)
                ).exists()

                if not refund_exists:
                    # 1. Lock and update wallet
                    wallet = Wallet.objects.select_for_update().get(
                        owner_id=user.id, 
                        type=w_type
                    )
                    
                    wallet.balance += instance.amount
                    wallet.save(update_fields=["balance"])
                    
                    # 2. Notify user (This also acts as our record that the refund happened)
                    Notification.objects.create(
                        user=user,
                        title="Withdrawal Failed - Refunded",
                        body=f"Your withdrawal {instance.id} failed. KES {instance.amount} returned to {w_type} wallet.",
                        notification_type="WITHDRAWAL_FAILED"
                    )
                    print(f"SUCCESS: Refunded KES {instance.amount} to user {user.id}")

        except Exception as e:
            print(f"CRITICAL: Refund Error for Withdrawal {instance.id}: {e}")