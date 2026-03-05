from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import MpesaTransaction
from wallets.models import Wallet
from ledger.models import LedgerAccount, LedgerEntry, SYSTEM_PLATFORM_ID
from notifications.models import Notification
from deposit.models import Deposit
from finance.mappings import get_ledger_account_type_for_wallet

@receiver(post_save, sender=MpesaTransaction)
def handle_mpesa_success(sender, instance, created, **kwargs):
    """
    Handles successful M-Pesa payments.
    UUID Safe: Uses Deposit status to prevent double-processing.
    """
    # 1. Terminal condition check
    if instance.status != "SUCCESS":
        return

    try:
        with transaction.atomic():
            # select_for_update() locks the row so only one process handles this success
            deposit = (
                Deposit.objects.select_for_update()
                .select_related("user")
                .get(mpesa_reference=instance)
            )

            # IDEMPOTENCY GUARD: 
            # If the Deposit is already SUCCESS, we've already done the ledger/wallet math.
            if deposit.status == "SUCCESS":
                return 

            # Start State Transition
            deposit.status = "SUCCESS"
            deposit.save(update_fields=["status"])

            # Identify target accounts via central mapping
            target_wallet_type = deposit.target_wallet
            target_ledger_type = get_ledger_account_type_for_wallet(target_wallet_type)
            system_id = SYSTEM_PLATFORM_ID

            # Lock accounts during the balance shift
            user_ledger = LedgerAccount.objects.select_for_update().get(
                owner_id=deposit.user.id,
                account_type=target_ledger_type,
            )

            system_ledger, _ = LedgerAccount.objects.select_for_update().get_or_create(
                owner_id=system_id,
                account_type="PLATFORM_REVENUE",
                defaults={"balance": 0},
            )
            system_ledger.balance += deposit.amount
            system_ledger.save(update_fields=["balance"])

            # 4. Record the Ledger Entry
            ledger_move = LedgerEntry.create_transaction(
                debit_acc=system_ledger,
                credit_acc=user_ledger,
                amount=deposit.amount,
                ref=f"DEP-{instance.external_txn_id}",
                desc=f"M-Pesa Top-up to {target_wallet_type}"
            )

            # 5. Mirror to Wallet
            wallet = Wallet.objects.select_for_update().get(
                owner_id=deposit.user.id,
                type=target_wallet_type,
            )
            wallet.balance += deposit.amount
            wallet.save(update_fields=["balance"])

            # 6. Finalize Deposit metadata
            deposit.ledger_entry = ledger_move
            deposit.save(update_fields=["ledger_entry"])

            # Notification
            Notification.objects.create(
                user=deposit.user,
                title="Top-up Successful",
                body=f"KES {deposit.amount} added to your {target_wallet_type} wallet.",
                notification_type="TOPUP_SUCCESS",
                data={"transaction_id": instance.external_txn_id}
            )

    except Deposit.DoesNotExist:
        # This happens if the STK push was initiated but the Deposit record was lost
        pass

@receiver(post_save, sender=MpesaTransaction)
def handle_mpesa_reversal_logic(sender, instance, created, **kwargs):
    """
    Handles Reversals or Failures.
    UUID Safe: Ensures reversal only happens if money was previously added.
    """
    if instance.status not in ["REVERSED", "FAILED"]:
        return

    try:
        with transaction.atomic():
            deposit = (
                Deposit.objects.select_for_update()
                .select_related("user")
                .get(mpesa_reference=instance)
            )

            # CRITICAL CHECK: We only reverse if the deposit was previously SUCCESSful.
            # If it was still PENDING or already REVERSED, we skip.
            if deposit.status != "SUCCESS":
                return

            # 1. Update Deposit status
            deposit.status = "REVERSED"
            deposit.save(update_fields=["status"])

            # 2. Identify Ledger Accounts
            target_ledger_type = get_ledger_account_type_for_wallet(deposit.target_wallet)
            
            user_ledger = LedgerAccount.objects.select_for_update().get(
                owner_id=deposit.user.id, account_type=target_ledger_type
            )
            system_ledger = LedgerAccount.objects.select_for_update().get(
                owner_id=SYSTEM_PLATFORM_ID, account_type="PLATFORM_REVENUE"
            )

            # 3. Create Reverse Ledger Entry (Debit User, Credit System)
            LedgerEntry.create_transaction(
                debit_acc=user_ledger,
                credit_acc=system_ledger,
                amount=deposit.amount,
                ref=f"REV-{instance.external_txn_id}",
                desc=f"Reversal of M-Pesa Txn: {instance.external_txn_id}",
            )

            # 4. Deduct from Wallet
            wallet = Wallet.objects.select_for_update().get(
                owner_id=deposit.user.id, type=deposit.target_wallet
            )
            
            # Note: We allow balance to go negative if the money was already spent
            # to maintain ledger honesty with the bank.
            wallet.balance -= deposit.amount
            wallet.save(update_fields=["balance"])

            # 5. Notify the User
            Notification.objects.create(
                user=deposit.user,
                title="Deposit Reversed",
                body=f"Your deposit of KES {deposit.amount} was reversed by M-Pesa.",
                notification_type="REVERSAL",
            )

    except Deposit.DoesNotExist:
        pass