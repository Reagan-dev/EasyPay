from django.contrib import admin
from django.utils import timezone
from .models import PaymentIntent

@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    # 1. Monitoring the "Pulse" of sales
    list_display = (
        'id', 
        'business', 
        'terminal_location', 
        'amount', 
        'status', 
        'expires_at', 
        'created_at'
    )
    
    # 2. Filters to find bottlenecks
    list_filter = ('status', 'business', 'created_at')
    
    # 3. Search by Business name or Payer ID
    search_fields = ('business__name', 'payer_id', 'id')
    
    # 4. Security: Keep financial intents mostly read-only
    readonly_fields = ('id', 'created_at', 'expires_at')
    
    # 5. Maintenance Actions
    actions = ['delete_old_expired_intents']
    
    # 6. Organization (Detail Page)
    fieldsets = (
        ('Context', {
            'fields': ('id', 'business', 'terminal')
        }),
        ('Financial Detail', {
            'fields': ('amount', 'status')
        }),
        ('Payer Info (Post-Scan)', {
            'fields': ('payer_id', 'payer_type'),
            'description': 'Filled once a student or customer scans the intent.'
        }),
        ('Timing', {
            'fields': ('expires_at', 'created_at')
        }),
    )

    # --- Helper Methods ---

    def terminal_location(self, obj):
        return obj.terminal.location
    terminal_location.short_description = "Terminal"

    # --- Custom Actions ---

    @admin.action(description="Cleanup: Delete intents expired more than 7 days ago")
    def delete_old_expired_intents(self, request, queryset):
        """
        Custom action to wipe out stale data. 
        Target: records with status EXPIRED/CANCELLED older than 1 week.
        """
        one_week_ago = timezone.now() - timezone.timedelta(days=7)
        
        old_intents = PaymentIntent.objects.filter(
            status__in=['EXPIRED', 'CANCELLED'],
            expires_at__lt=one_week_ago
        )
        
        count = old_intents.count()
        old_intents.delete()
        
        self.message_user(
            request, 
            f"Successfully purged {count} stale payment intents from the database.",
            level='success'
        )