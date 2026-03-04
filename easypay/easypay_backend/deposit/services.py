import requests
import base64
from datetime import datetime
from django.conf import settings
from mpesa.models import MpesaTransaction
from .models import Deposit
from ledger.models import LedgerAccount, LedgerEntry
from withdrawal.models import Withdrawal
import uuid

class MpesaService:
    @staticmethod
    def get_access_token():
        """Fetches the OAuth2 access token from Safaricom."""
        url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
        
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

    # --- DEPOSIT LOGIC (STK PUSH) ---
    @staticmethod
    def initiate_stk_push(user, amount, phone, target_wallet):
        """Triggers the M-Pesa Express (STK Push) prompt on the user's phone."""
        phone = str(phone).strip().replace("+", "")
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        
        deposit = Deposit.objects.create(
            user=user,
            amount=amount,
            target_wallet=target_wallet,
            status="PENDING"
        )

        access_token = MpesaService.get_access_token()
        if not access_token:
            print("ERROR: Could not fetch M-Pesa Access Token.")
            return None

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = MpesaService.generate_password(timestamp)
        headers = {"Authorization": f"Bearer {access_token}"}
        
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(float(amount)),
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": f"DEP{deposit.id}"[:12],
            "TransactionDesc": "EasyPay Deposit"
        }

        url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                print(f"M-Pesa API Error {response.status_code}: {response.text}")
                return None
                
            stk_response = response.json()
        except Exception as e:
            print(f"CRITICAL ERROR in STK Push: {str(e)}")
            return None

        if stk_response.get("ResponseCode") == "0":
            mpesa_txn = MpesaTransaction.objects.create(
                merchant_request_id=stk_response["MerchantRequestID"],
                checkout_request_id=stk_response["CheckoutRequestID"],
                phone=phone,
                amount=amount,
                user_id=user.id,
                status="PENDING"
            )
            deposit.mpesa_reference = mpesa_txn
            deposit.save()
            return mpesa_txn
        
        return None

    # --- WITHDRAWAL LOGIC (B2C) ---
    @staticmethod
    def initiate_b2c_withdrawal(withdrawal):
        """Sends money from the Business Shortcode to the Customer phone."""
        access_token = MpesaService.get_access_token()
        if not access_token:
            return {"ResponseCode": "1", "ResponseDescription": "Failed to get access token"}
        
        phone = str(withdrawal.phone_number).strip().replace("+", "")
        if phone.startswith("0"):
            phone = "254" + phone[1:]

        url = f"{settings.MPESA_BASE_URL}/mpesa/b2c/v3/paymentrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Note: B2C results usually go to a different ResultURL than STK Push
        # We derive it here from your existing callback setting
        withdrawal_callback = settings.MPESA_CALLBACK_URL.replace('mpesa/callback/', 'withdrawals/callback/')

        originator_id = (str(uuid.uuid4())[:32]).upper()  # Unique Originator ID for tracking
        
        payload = {
            "OriginatorConversationID": originator_id,
            "InitiatorName": settings.MPESA_INITIATOR_NAME,
            "SecurityCredential": settings.MPESA_INITIATOR_PASSWORD,
            "CommandID": "BusinessPayment",
            "Amount": int(withdrawal.amount),
            "PartyA": settings.MPESA_B2C_SHORTCODE,
            "PartyB": phone,
            "Remarks": f"WDL {withdrawal.id}",
            "QueueTimeOutURL": withdrawal_callback,
            "ResultURL": withdrawal_callback,
            "Occasion": "Withdrawal"
        }
        
        response = requests.post(url, json=payload, headers=headers)

        print("DEBUG B2C Status:", response.status_code)
        print("DEBUG B2C Raw:", response.text)

        if response.status_code != 200:
            return {
                "ResponseCode": "1",
                "ResponseDescription": f"HTTP {response.status_code}: {response.text}"
            }

        try:
            return response.json()
        except ValueError:
            return {
                "ResponseCode": "1",
                "ResponseDescription": "Invalid JSON response from Safaricom",
                "Raw": response.text
            }