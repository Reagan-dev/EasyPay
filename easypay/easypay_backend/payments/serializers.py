from rest_framework import serializers
from .models import PaymentIntent
from merchants.models import BusinessTerminal

class PaymentIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentIntent
        fields = [
            'id', 'business', 'terminal', 'amount', 
            'status', 'payer_id', 'payer_type', 
            'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'business', 'status', 'payer_id', 'payer_type', 'expires_at', 'created_at']

    def validate_terminal(self, value):
        # Ensure the terminal is active and belongs to the authenticated business user
        user = self.context['request'].user
        if not BusinessTerminal.objects.filter(id=value.id, business__user=user).exists():
            raise serializers.ValidationError("Unauthorized: This terminal does not belong to your business.")
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("The transaction amount must be positive.")
        return value