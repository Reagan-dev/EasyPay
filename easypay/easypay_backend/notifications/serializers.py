from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    # We make created_at human-readable for the UI
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'body', 'notification_type', 
            'is_read', 'data', 'created_at', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at']

    def get_time_ago(self, obj):
        # Optional: You could use a library like 'arrow' or 'humanize' here
        return obj.created_at.strftime("%b %d, %H:%M")