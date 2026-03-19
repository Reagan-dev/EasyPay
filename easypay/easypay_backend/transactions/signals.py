from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Transaction
from ledger.models import LedgerAccount, LedgerEntry, SYSTEM_PLATFORM_ID
from wallets.models import Wallet
from notifications.models import Notification
from decimal import Decimal
from django.contrib.auth import get_user_model
from merchants.models import Business
from accounts.models import User

@receiver(post_save, sender=Transaction)
def handle_transaction_success(sender, instance, created, **kwargs):
    # Important: Check status transition to avoid re-processing
    if instance.status == "SUCCESS" and not instance.ledger_entry:
        try:
            with transaction.atomic():
                # --- DEBUGGING: See what is being searched ---
                PAYER_LEDGER_MAP = {
                    ("CUSTOMER", "PERSONAL"): "CUSTOMER_MAIN",
                    ("STUDENT", "MEAL"): "STUDENT_MEAL",
                    ("STUDENT", "POCKET"): "STUDENT_POCKET",
                }
                payer_type_acc = PAYER_LEDGER_MAP.get(
                    (instance.payer_type, instance.wallet_type)
                )
                print(f"DEBUG: Looking for Payer Ledger: ID={instance.payer_id}, Type={payer_type_acc}")
                print(f"DEBUG: Looking for Biz Ledger: ID={instance.user.id}, Type=BUSINESS_PAYOUT")
                # ---------------------------------------------

                # Fetch Ledger Accounts 
                payer_ledger = LedgerAccount.objects.get(
                    owner_id=instance.payer_id,
                    account_type=payer_type_acc
                )
                
                business_ledger = LedgerAccount.objects.get(
                    owner_id=instance.user.id,
                    account_type="BUSINESS_PAYOUT"
                )

                revenue_ledger = LedgerAccount.objects.get(
                    owner_id=SYSTEM_PLATFORM_ID,
                    account_type="PLATFORM_REVENUE"
                )

                # Strict Decimal Math
                amount = Decimal(str(instance.amount))
                fee = Decimal(str(instance.platform_fee))
                net_amount = amount - fee

                # Ledger Entries (The Audit Trail)
                entry = LedgerEntry.create_transaction(
                    debit_acc=payer_ledger,
                    credit_acc=business_ledger,
                    amount=net_amount,
                    ref=f"TXN-BIZ-{instance.id}",
                    desc=f"Payment to {instance.business.name}"
                )

                LedgerEntry.create_transaction(
                    debit_acc=payer_ledger,
                    credit_acc=revenue_ledger,
                    amount=fee,
                    ref=f"TXN-FEE-{instance.id}",
                    desc=f"Platform Fee for TXN-{instance.id}"
                )

                # 4. Update Wallets (Fetch existing wallets)
                payer_wallet = Wallet.objects.select_for_update().get(
                    owner_id=instance.payer_id,
                    type=instance.wallet_type,
                )
                
                # Convert current balance to decimal safely
                p_bal = Decimal(str(payer_wallet.balance))
                if p_bal < amount:
                    raise ValueError("Insufficient wallet balance.")
                
                payer_wallet.balance = p_bal - amount
                payer_wallet.save(update_fields=["balance"])

                biz_wallet = Wallet.objects.select_for_update().get(
                    owner_id=instance.user.id,
                    type="SETTLEMENT",
                )
                biz_wallet.balance = Decimal(str(biz_wallet.balance)) + net_amount
                biz_wallet.save(update_fields=["balance"])

                # 5. Finalize Transaction (Using .update to avoid triggering this signal again)
                Transaction.objects.filter(id=instance.id).update(ledger_entry=entry)

                # 6. Notifications
                User = get_user_model()
                payer_user = User.objects.get(id=instance.payer_id)
                
                Notification.objects.create(
                    user=payer_user,
                    title="Payment Successful",
                    body=f"Paid KES {amount} to {instance.business.name}",
                    notification_type="PAYMENT_SENT"
                )

                if instance.business.user:
                    Notification.objects.create(
                        user=instance.business.user,
                        title="New Sale Received",
                        body=f"Received KES {net_amount}",
                        notification_type="PAYMENT_RECEIVED"
                    )

        except Exception as e:
            print(f"!!! Transaction Signal Error: {e}")