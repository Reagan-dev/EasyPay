# mpesa/utils.py
import requests
import base64
from django.conf import settings
from datetime import datetime

class MpesaClient:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.base_url = "https://sandbox.safaricom.co.ke" # Change to api.safaricom.co.ke for production

    def get_token(self):
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
        return response.json().get('access_token')
    
    def stk_push(self, phone_number, amount, callback_url, account_ref):
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
        ).decode()

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": account_ref,
            "TransactionDesc": "EasyPay Deposit"
        }

        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest", 
            json=payload, 
            headers=headers
        )
        return response.json()
    
    def b2c_payout(self, phone_number, amount, occasion):
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {
            "InitiatorName": settings.MPESA_INITIATOR_NAME,
            "SecurityCredential": settings.MPESA_INITIATOR_PASSWORD, # Encrypted in production
            "CommandID": "BusinessPayment",
            "Amount": amount,
            "PartyA": settings.MPESA_B2C_SHORTCODE,
            "PartyB": phone_number,
            "Remarks": "EasyPay Withdrawal",
            "QueueTimeOutURL": "https://yourdomain.com/api/mpesa/b2c/timeout/",
            "ResultURL": "https://yourdomain.com/api/mpesa/b2c/result/",
            "Occasion": occasion
        }

        response = requests.post(
            f"{self.base_url}/mpesa/b2c/v1/paymentrequest", 
            json=payload, 
            headers=headers
        )
        return response.json()