from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import MpesaTransaction
from wallets.models import Wallet
from ledger.models import LedgerAccount, LedgerEntry
from notifications.models import Notification
from deposit.models import Deposit


@receiver(post_save, sender=MpesaTransaction)
def handle_mpesa_success(sender, instance, created, **kwargs):
    if instance.status == "SUCCESS":
        try:
            deposit = Deposit.objects.get(mpesa_reference=instance)
            if deposit.status == "SUCCESS":
                return 

            with transaction.atomic():
                deposit.status = "SUCCESS"
                deposit.save()

                # 1. Use the target_wallet chosen by the user during the deposit request
                target_wallet_type = deposit.target_wallet 
                
                # 2. Map target_wallet to target_ledger_type
                # Students: MEAL -> STUDENT_MEAL, POCKET -> STUDENT_POCKET
                # Others: PERSONAL -> CUSTOMER_MAIN, SETTLEMENT -> BUSINESS_PAYOUT
                if target_wallet_type == "MEAL":
                    target_ledger_type = "STUDENT_MEAL"
                elif target_wallet_type == "POCKET":
                    target_ledger_type = "STUDENT_POCKET"
                elif target_wallet_type == "SETTLEMENT":
                    target_ledger_type = "BUSINESS_PAYOUT"
                else:
                    target_ledger_type = "CUSTOMER_MAIN"

                # 3. Identify Ledger Accounts
                system_id = "00000000-0000-0000-0000-000000000000"
                
                user_ledger = LedgerAccount.objects.get(
                    owner_id=deposit.user.id, 
                    account_type=target_ledger_type
                )
            
                
                system_ledger, _ = LedgerAccount.objects.get_or_create(
                    owner_id=system_id,
                    account_type="PLATFORM_REVENUE", 
                    defaults={'balance': 0}
                )

                # 4. Record the Ledger Entry
                ledger_move = LedgerEntry.create_transaction(
                    debit_acc=system_ledger,
                    credit_acc=user_ledger,
                    amount=deposit.amount,
                    ref=f"DEP-{instance.external_txn_id}",
                    desc=f"M-Pesa Top-up to {target_wallet_type}"
                )

                # 5. Update the Wallet (Digital Mirror)
                wallet = Wallet.objects.get(
                    owner_id=deposit.user.id, 
                    type=target_wallet_type
                )
                wallet.balance += deposit.amount
                wallet.save()

                # 6. Finalize Deposit and Notify
                deposit.ledger_entry = ledger_move
                deposit.save()

                Notification.objects.create(
                    user=deposit.user,
                    title="Top-up Successful",
                    body=f"KES {deposit.amount} added to your {target_wallet_type} wallet.",
                    notification_type="TOPUP_SUCCESS",
                    data={"transaction_id": instance.external_txn_id}
                )

        except Deposit.DoesNotExist:
            pass