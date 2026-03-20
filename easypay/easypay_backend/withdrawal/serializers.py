from rest_framework import serializers
from .models import Withdrawal
from wallets.models import Wallet
from rest_framework.exceptions import ValidationError
from finance.mappings import get_withdrawal_wallet_type_for_user


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ["id", "amount", "phone_number", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate(self, data):
        user = self.context["request"].user

        w_type = get_withdrawal_wallet_type_for_user(user)

        # Keep a lightweight existence check here for user feedback,
        # but authoritative balance checks happen inside the atomic block.
        if not Wallet.objects.filter(owner_id=user.id, type=w_type).exists():
            raise ValidationError("Source wallet not found.")

        return data