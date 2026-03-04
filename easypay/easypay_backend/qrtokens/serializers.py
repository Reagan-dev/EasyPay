from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import QRToken
from wallets.models import Wallet
from rest_framework.exceptions import ValidationError

class QRTokenCreateSerializer(serializers.ModelSerializer):
    # Field to specify which wallet the QR should draw from
    wallet_type = serializers.ChoiceField(choices=["MEAL", "POCKET", "PERSONAL"], write_only=True)

    class Meta:
        model = QRToken
        fields = ['id', 'amount', 'token_value', 'expires_at', 'status', 'wallet_type']
        read_only_fields = ['id', 'token_value', 'expires_at', 'status']

    def validate(self, data):
        user = self.context['request'].user
        amount = data.get('amount')
        wallet_type = data.get('wallet_type')

        # 1. Check if user has sufficient balance in the specified wallet
        try:
            wallet = Wallet.objects.get(owner_id=user.id, type=wallet_type)
            if wallet.balance < amount:
                raise ValidationError(f"Insufficient funds in {wallet_type} wallet.")
        except Wallet.DoesNotExist:
            raise ValidationError("Source wallet not found.")

        return data

    # qrtokens/serializers.py

    def create(self, validated_data):
        # 1. Pop wallet_type so it doesn't hit the DB (Prevents TypeError)
        validated_data.pop('wallet_type', None)

        # 2. Extract the student/customer/expires_at from validated_data
        # These are passed in from the serializer.save() in your view.
        student = validated_data.pop('student', None)
        customer = validated_data.pop('customer', None)
        expires_at = validated_data.pop('expires_at', None)

        # 3. Create the token
        # Because we explicitly pass student and customer, the 
        # NOT NULL constraint is satisfied.
        return QRToken.objects.create(
            student=student,
            customer=customer,
            expires_at=expires_at,
            **validated_data
        )