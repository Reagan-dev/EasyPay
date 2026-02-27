import requests
from django.conf import settings
from mpesa.models import MpesaTransaction
from .models import Deposit

class MpesaService:
    """
    Handles communication with Safaricom Daraja API.
    """
    @staticmethod
    def initiate_stk_push(user, amount, phone, target_wallet):
        # 1. Create a Pending Deposit record first
        deposit = Deposit.objects.create(
            user=user,
            amount=amount,
            target_wallet=target_wallet,
            status="PENDING"
        )

        # 2. Prepare Safaricom Request (Simplified logic)
        # In production, you'd generate the password/timestamp here
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Amount": amount,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": f"DEP-{deposit.id.hex[:6]}",
            "TransactionDesc": "EasyPay Top-up"
        }

        # 3. Call Safaricom API
        # response = requests.post(settings.MPESA_STK_URL, json=payload, headers=headers)
        # Mocking a successful initiation response:
        stk_response = {
            "MerchantRequestID": "REQ-123",
            "CheckoutRequestID": "CHK-456",
            "ResponseCode": "0"
        }

        if stk_response.get("ResponseCode") == "0":
            # 4. Create the MpesaTransaction bridge
            mpesa_txn = MpesaTransaction.objects.create(
                merchant_request_id=stk_response["MerchantRequestID"],
                checkout_request_id=stk_response["CheckoutRequestID"],
                phone=phone,
                amount=amount,
                user_id=user.id,
                status="PENDING"
            )
            
            # Link deposit to this mpesa txn
            deposit.mpesa_reference = mpesa_txn
            deposit.save()
            return mpesa_txn
        
        return None