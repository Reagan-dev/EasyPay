from rest_framework import serializers
from .models import MpesaTransaction

class MpesaTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaTransaction
        fields = '__all__'

# mpesa/serializers.py

class MpesaCallbackSerializer(serializers.Serializer):
    Body = serializers.DictField()

    def extract_data(self):
        stk_callback = self.validated_data['Body']['stkCallback']
        result_code = stk_callback.get('ResultCode')
        
        data = {
            'checkout_request_id': stk_callback.get('CheckoutRequestID'),
            'merchant_request_id': stk_callback.get('MerchantRequestID'),
            'raw_payload': self.validated_data,
            'result_code': result_code,  
            'status': 'SUCCESS' if result_code == 0 else 'FAILED'
        }

        if result_code == 0:
            items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            for item in items:
                name = item.get('Name')
                value = item.get('Value')
                if name == 'MpesaReceiptNumber': data['external_txn_id'] = value
                if name == 'Amount': data['amount'] = value
                if name == 'PhoneNumber': data['phone'] = value
        
        return data