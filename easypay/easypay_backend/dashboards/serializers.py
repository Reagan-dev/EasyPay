from rest_framework import serializers

class BaseDashboardSerializer(serializers.Serializer):
    """Common fields for all dashboards"""
    unread_notifications_count = serializers.IntegerField()
    account_status = serializers.CharField() # ACTIVE, FROZEN, etc.
    currency = serializers.CharField(default="KES")

class StudentDashboardSerializer(BaseDashboardSerializer):
    full_name = serializers.CharField()
    meal_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    pocket_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    today_spend = serializers.DecimalField(max_digits=12, decimal_places=2)
    active_qr_token = serializers.DictField(allow_null=True) # Current valid QR info
    recent_activity = serializers.ListField()

class MerchantDashboardSerializer(BaseDashboardSerializer):
    business_name = serializers.CharField()
    settlement_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    today_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    today_tx_count = serializers.IntegerField()
    pending_withdrawals_count = serializers.IntegerField()
    recent_sales = serializers.ListField()

class GuardianDashboardSerializer(BaseDashboardSerializer):
    personal_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_family_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    children = serializers.ListField()
    recent_personal_tx = serializers.ListField()