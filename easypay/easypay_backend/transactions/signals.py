from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Transaction
from ledger.models import LedgerAccount, LedgerEntry, SYSTEM_PLATFORM_ID
from wallets.models import Wallet
from notifications.models import Notification

@receiver(post_save, sender=Transaction)
def handle_transaction_success(sender, instance, created, **kwargs):
    # We only act when a transaction is marked SUCCESS and hasn't been ledgered yet
    if instance.status == "SUCCESS" and not instance.ledger_entry:
        try:
            with transaction.atomic():
                # 1. Get Ledger Accounts
                # The Payer (Student or Customer)
                payer_ledger = LedgerAccount.objects.get(
                    owner_id=instance.payer_id,
                    account_type=f"{instance.payer_type}_{instance.wallet_type}"
                )
                
                # The Business Settlement Account
                business_ledger = LedgerAccount.objects.get(
                    owner_id=instance.business.id,
                    account_type="BUSINESS_PAYOUT"
                )
                
                # The EasyPay Revenue Account (System Account)
                # Note: You should have a constant for your System User ID
                system_id = SYSTEM_PLATFORM_ID
                revenue_ledger = LedgerAccount.objects.get(
                    owner_id=system_id,
                    account_type="PLATFORM_REVENUE"
                )

                # 2. Execute Ledger Moves
                # Move the Net Amount to the Business
                net_amount = instance.amount - instance.platform_fee
                
                entry = LedgerEntry.create_transaction(
                    debit_acc=payer_ledger,
                    credit_acc=business_ledger,
                    amount=net_amount,
                    ref=f"TXN-BIZ-{instance.id}",
                    desc=f"Payment to {instance.business.name}"
                )

                # Move the Fee to EasyPay Revenue
                LedgerEntry.create_transaction(
                    debit_acc=payer_ledger,
                    credit_acc=revenue_ledger,
                    amount=instance.platform_fee,
                    ref=f"TXN-FEE-{instance.id}",
                    desc=f"Platform Fee for TXN-{instance.id}"
                )

                # 3. Update Wallets (The Digital Mirror)
                # Update Payer Wallet
                payer_wallet = Wallet.objects.get(
                    owner_id=instance.payer_id,
                    type=instance.wallet_type
                )
                payer_wallet.balance -= instance.amount
                payer_wallet.save()

                # Update Business Wallet
                biz_wallet = Wallet.objects.get(
                    owner_id=instance.business.id,
                    type="SETTLEMENT"
                )
                biz_wallet.balance += net_amount
                biz_wallet.save()

                # 4. Finalize Transaction Record
                instance.ledger_entry = entry
                instance.save()

                # 5. Send Notifications
                # To Payer
                Notification.objects.create(
                    user=payer_wallet.user, # Assumes Wallet has a user link or you fetch it
                    title="Payment Successful",
                    body=f"Paid KES {instance.amount} to {instance.business.name}",
                    notification_type="PAYMENT_SENT"
                )
                
                # To Business Owner
                Notification.objects.create(
                    user=instance.business.user,
                    title="New Sale Received",
                    body=f"You received KES {net_amount} (Fee: KES {instance.platform_fee})",
                    notification_type="PAYMENT_RECEIVED"
                )

        except Exception as e:
            # In production, use a logger here
            print(f"Transaction Signal Error: {e}")