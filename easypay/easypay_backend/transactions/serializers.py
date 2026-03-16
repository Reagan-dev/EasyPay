from rest_framework import serializers
from .models import Transaction
from qrtokens.models import QRToken
from payments.models import PaymentIntent
from wallets.models import Wallet

class SaleExecutionSerializer(serializers.ModelSerializer):
    token_value = serializers.CharField(write_only=True)
    intent_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Transaction
        # We only need these from the frontend; the rest is derived server-side
        fields = ['id', 'token_value', 'intent_id', 'wallet_type']
        read_only_fields = ['id']

    def validate(self, data):
        # 1. Validate the Payment Intent (The Terminal's Request)
        try:
            intent = PaymentIntent.objects.get(id=data['intent_id'])
        except PaymentIntent.DoesNotExist:
            raise serializers.ValidationError("Payment request (Intent) not found.")

        if not intent.is_active:
            raise serializers.ValidationError("This payment request has expired or was already completed.")

        # 2. Validate the QR Token (The Student's Wallet Access)
        try:
            token = QRToken.objects.get(token_value=data['token_value'])
        except QRToken.DoesNotExist:
            raise serializers.ValidationError("Invalid QR code scanned.")

        if not token.is_valid:
            raise serializers.ValidationError("This QR code has expired or been used.")

        # 3. Security Check: Amount Mismatch Prevention
        if token.amount != intent.amount:
            raise serializers.ValidationError(
                f"Amount mismatch. QR is for {token.amount} but Terminal requested {intent.amount}."
            )

        # 4. Final Balance Check
        payer_user_id = token.student.user.id if token.student else token.customer.user.id
        try:
            wallet = Wallet.objects.get(owner_id=payer_user_id, type=data['wallet_type'])
            if wallet.balance < intent.amount:
                raise serializers.ValidationError(f"Insufficient funds in {data['wallet_type']} wallet.")
        except Wallet.DoesNotExist:
            raise serializers.ValidationError(f"Wallet type {data['wallet_type']} not found for this user.")

        # Attach resolved objects for use in the view
        data['token_object'] = token
        data['intent_object'] = intent
        data['payer_user_id'] = payer_user_id
        return data
    
    def create(self, validated_data):
        validated_data.pop('token_value', None)
        validated_data.pop('intent_id', None)
        validated_data.pop('token_object', None)
        validated_data.pop('intent_object', None)
        validated_data.pop('payer_user_id', None)
        
        # 2. validated_data only contains real Transaction model fields
        return super().create(validated_data)