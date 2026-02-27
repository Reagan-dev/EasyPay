from rest_framework import serializers
from .models import Withdrawal
from wallets.models import Wallet

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['id', 'amount', 'phone_number', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        amount = data.get('amount')

        # Identify target wallet based on role
        if hasattr(user, 'business'):
            w_type = "SETTLEMENT"
        elif hasattr(user, 'student_profile'):
            w_type = "POCKET" # Students can ONLY withdraw from Pocket
        else:
            w_type = "PERSONAL"

        try:
            wallet = Wallet.objects.get(owner_id=user.id, type=w_type)
            if wallet.balance < amount:
                raise serializers.ValidationError(f"Insufficient funds in your {w_type} wallet.")
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Source wallet not found.")

        return data