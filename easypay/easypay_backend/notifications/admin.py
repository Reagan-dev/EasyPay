from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # 1. Quick look at what's happening across the platform
    list_display = (
        'user_phone', 
        'title', 
        'notification_type', 
        'is_read', 
        'created_at'
    )
    
    # 2. Vital filters for troubleshooting
    # Filter by type (e.g., see how many LOW_BALANCE alerts went out today)
    list_filter = ('notification_type', 'is_read', 'created_at')
    
    # 3. Search by User details or message content
    search_fields = ('user__phone', 'user__email', 'title', 'body')
    
    # 4. JSON metadata handling
    # We keep 'data' and 'created_at' as read-only to see exactly what was sent
    readonly_fields = ('id', 'created_at', 'data')
    
    # 5. UI Organization
    fieldsets = (
        ('Recipient', {
            'fields': ('user', 'id')
        }),
        ('Message Content', {
            'fields': ('notification_type', 'title', 'body', 'is_read')
        }),
        ('Payload & Metadata', {
            'fields': ('data', 'created_at'),
            'description': 'Extra context (like transaction IDs) stored in the notification.'
        }),
    )

    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = "User Phone"
