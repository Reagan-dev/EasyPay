from rest_framework import serializers
from .models import Deposit

class DepositRequestSerializer(serializers.ModelSerializer):
    # We add phone_number as a write-only field for the STK Push
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = Deposit
        fields = ['amount', 'target_wallet', 'phone_number', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

    def validate_amount(self, value):
        if value < 10:
            raise serializers.ValidationError("The minimum deposit amount is KES 10.00")
        return value

    def validate_phone_number(self, value):
        # Basic Kenyan phone validation (254...)
        if not value.startswith('0') or len(value) > 12:
            raise serializers.ValidationError("Phone number must be in the format 0XXXXXXXXX")
        return value