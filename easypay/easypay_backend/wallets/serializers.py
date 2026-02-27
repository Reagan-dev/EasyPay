from rest_framework import serializers
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    # Using DecimalField ensures the frontend doesn't suffer from floating point errors
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    # Human-readable labels for the UI
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Wallet
        fields = [
            'id', 
            'owner_type', 
            'owner_id', 
            'type', 
            'type_display',
            'balance', 
            'is_withdrawable', 
            'created_at'
        ]
        # Everything is read-only because Wallets are managed by System Signals
        read_only_fields = fields