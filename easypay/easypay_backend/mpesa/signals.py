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
    # Transition-aware: only act when we move into SUCCESS
    if instance.status != "SUCCESS":
        return

    previous_status = None
    if not created and instance.pk:
        try:
            previous_status = sender.objects.only("status").get(pk=instance.pk).status
        except sender.DoesNotExist:
            previous_status = None

    if previous_status == "SUCCESS":
        # Already processed success
        return

    try:
        with transaction.atomic():
            # Lock the deposit row to make success handling idempotent and race-safe
            deposit = (
                Deposit.objects.select_for_update()
                .select_related("user")
                .get(mpesa_reference=instance)
            )
            if deposit.status == "SUCCESS" and deposit.ledger_entry_id:
                # Already fully processed
                return

            deposit.status = "SUCCESS"
            deposit.save(update_fields=["status"])

            # 1. Use the target_wallet chosen by the user during the deposit request
            target_wallet_type = deposit.target_wallet

            # 2. Map target_wallet to target_ledger_type via central mapping
            target_ledger_type = get_ledger_account_type_for_wallet(target_wallet_type)

            # 3. Identify Ledger Accounts
            system_id = SYSTEM_PLATFORM_ID

            user_ledger = LedgerAccount.objects.select_for_update().get(
                owner_id=deposit.user.id,
                account_type=target_ledger_type,
            )

            system_ledger, _ = LedgerAccount.objects.select_for_update().get_or_create(
                owner_id=system_id,
                account_type="PLATFORM_REVENUE",
                defaults={"balance": 0},
            )

            # 4. Record the Ledger Entry (idempotent by reference)
            ledger_move = LedgerEntry.create_transaction(
                debit_acc=system_ledger,
                credit_acc=user_ledger,
                amount=deposit.amount,
                ref=f"DEP-{instance.external_txn_id}",
                desc=f"M-Pesa Top-up to {target_wallet_type}"
            )

            # 5. Update the Wallet (Digital Mirror) with locking
            wallet = Wallet.objects.select_for_update().get(
                owner_id=deposit.user.id,
                type=target_wallet_type,
            )
            wallet.balance += deposit.amount
            wallet.save(update_fields=["balance"])

            # 6. Finalize Deposit and Notify
            deposit.ledger_entry = ledger_move
            deposit.save(update_fields=["ledger_entry"])

            Notification.objects.create(
                user=deposit.user,
                title="Top-up Successful",
                body=f"KES {deposit.amount} added to your {target_wallet_type} wallet.",
                notification_type="TOPUP_SUCCESS",
                data={"transaction_id": instance.external_txn_id}
            )

    except Deposit.DoesNotExist:
        pass

@receiver(post_save, sender=MpesaTransaction)
def handle_mpesa_reversal_logic(sender, instance, created, **kwargs):
    # We only care if the status is now REVERSED or FAILED
    if instance.status not in ["REVERSED", "FAILED"]:
        return

    previous_status = None
    if not created and instance.pk:
        try:
            previous_status = sender.objects.only("status").get(pk=instance.pk).status
        except sender.DoesNotExist:
            previous_status = None

    # Only act on the first transition into a terminal reversed/failed state
    if previous_status in ["REVERSED", "FAILED"]:
        return

    try:
        with transaction.atomic():
            deposit = (
                Deposit.objects.select_for_update()
                .select_related("user")
                .get(mpesa_reference=instance)
            )

            # CRITICAL CHECK: Only reverse if the ledger already added the money
            if deposit.status != "SUCCESS":
                return

            # 1. Update Deposit to the new status
            deposit.status = "REVERSED"
            deposit.save(update_fields=["status"])

            # 2. Identify Ledger Accounts (Same as success but roles swapped)
            system_id = SYSTEM_PLATFORM_ID

            # Dynamic mapping for the user ledger via central mapping
            target_ledger_type = get_ledger_account_type_for_wallet(deposit.target_wallet)

            user_ledger = LedgerAccount.objects.select_for_update().get(
                owner_id=deposit.user.id, account_type=target_ledger_type
            )
            system_ledger = LedgerAccount.objects.select_for_update().get(
                owner_id=system_id, account_type="PLATFORM_REVENUE"
            )

            # 3. Create Reverse Ledger Entry
            # We DEBIT the user (take away) and CREDIT the system (return funds)
            LedgerEntry.create_transaction(
                debit_acc=user_ledger,
                credit_acc=system_ledger,
                amount=deposit.amount,
                ref=f"REV-{instance.external_txn_id}",
                desc=f"Reversal of M-Pesa Txn: {instance.external_txn_id}",
            )

            # 4. Deduct from Wallet with locking and safety
            wallet = Wallet.objects.select_for_update().get(
                owner_id=deposit.user.id, type=deposit.target_wallet
            )
            if wallet.balance < deposit.amount:
                raise ValueError("Reversal would overdraw wallet; aborting.")
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
        print(f"Signal Error: No Deposit found for M-Pesa ID {instance.id}")