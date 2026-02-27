from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import QRToken
from wallets.models import Wallet

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
                raise serializers.ValidationError(f"Insufficient funds in {wallet_type} wallet.")
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Source wallet not found.")

        return data