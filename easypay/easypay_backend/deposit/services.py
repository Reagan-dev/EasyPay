import requests
import base64
from datetime import datetime
from django.conf import settings
from mpesa.models import MpesaTransaction
from .models import Deposit

class MpesaService:
    @staticmethod
    def get_access_token():
        url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    
        # ADD THESE DEBUG LINES:
        print(f"DEBUG: Status Code: {response.status_code}")
        print(f"DEBUG: Raw Response: '{response.text}'") 
    
        if response.status_code != 200:
           return None
        
        return response.json().get('access_token')
    @staticmethod
    def generate_password(timestamp):
        """Generates the base64 encoded password for STK Push."""
        data_to_encode = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
        encoded_string = base64.b64encode(data_to_encode.encode())
        return encoded_string.decode('utf-8')

    @staticmethod
    def initiate_stk_push(user, amount, phone, target_wallet):
        # 1. Clean the Phone Number (Crucial for Safaricom)
        # Convert 07... or +254... to 2547...
        phone = str(phone).strip().replace("+", "")
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        
        # 2. Create a Pending Deposit record
        deposit = Deposit.objects.create(
            user=user,
            amount=amount,
            target_wallet=target_wallet,
            status="PENDING"
        )

        # 3. Prepare Credentials
        access_token = MpesaService.get_access_token()
        if not access_token:
            print("ERROR: Could not fetch M-Pesa Access Token.")
            return None

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = MpesaService.generate_password(timestamp)
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 4. Prepare Payload (Strictly following Daraja specs)
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(float(amount)),  # Must be an integer
            "PartyA": phone,               # Must be 2547XXXXXXXX
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": f"DEP{deposit.id}"[:12], # Max 12 chars
            "TransactionDesc": "EasyPay Deposit"
        }

        # 5. Call API with Error Handling
        url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            # If Safaricom sends an error (like 400), this prevents a crash
            if response.status_code != 200:
                print(f"M-Pesa API Error {response.status_code}: {response.text}")
                return None
                
            stk_response = response.json()
        except Exception as e:
            print(f"CRITICAL ERROR in STK Push: {str(e)}")
            return None

        # 6. Handle Successful Handshake
        if stk_response.get("ResponseCode") == "0":
            mpesa_txn = MpesaTransaction.objects.create(
                merchant_request_id=stk_response["MerchantRequestID"],
                checkout_request_id=stk_response["CheckoutRequestID"],
                phone=phone,
                amount=amount,
                user=user,
                status="PENDING"
            )
            deposit.mpesa_reference = mpesa_txn
            deposit.save()
            return mpesa_txn
        
        return None