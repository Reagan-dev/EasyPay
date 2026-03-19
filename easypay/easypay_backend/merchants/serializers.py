from rest_framework import serializers
from .models import Business, BusinessTerminal
from accounts.serializers import UserSerializer

class BusinessTerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessTerminal
        fields = ['id', 'business', 'device_id', 'location', 'is_online', 'created_at']
        read_only_fields = ['id', 'created_at']

class BusinessProfileSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    # This nests the terminals so the owner can see all their POS points
    terminals = BusinessTerminalSerializer(many=True, read_only=True)

    class Meta:
        model = Business
        fields = [
            'id', 'user_details', 'name', 'category_code', 
            'mpesa_till_number', 'is_active', 'terminals', 'created_at'
        ]
        read_only_fields = ['id', 'is_active', 'created_at']

    def validate_category_code(self, value):
        # Enforcing 'FOOD' specification for now
        allowed_categories = ['FOOD', 'OTHERS']
        if value.upper() not in allowed_categories:
            raise serializers.ValidationError(f"Invalid category. Must be one of {allowed_categories}")
        return value.upper()