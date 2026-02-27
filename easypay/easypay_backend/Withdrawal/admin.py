from django.contrib import admin
from .models import Withdrawal

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    # 1. Monitoring the "Outflow" of cash
    list_display = (
        'id_short', 
        'user_phone', 
        'amount', 
        'fee', 
        'net_payout', 
        'status', 
        'created_at'
    )
    
    # 2. Vital filters to manage operations
    # 'PROCESSING' is the one to watch—it means the B2C request is out but not confirmed
    list_filter = ('status', 'created_at')
    
    # 3. Search by Phone, Reference, or ID
    search_fields = ('phone_number', 'external_reference', 'user__phone', 'id')
    
    # 4. Security: Read-only fields for finalized transactions
    # We don't want someone manually changing the amount of a withdrawal
    readonly_fields = ('id', 'amount', 'fee', 'ledger_entry', 'created_at', 'updated_at')
    
    # 5. Detail View Organization
    fieldsets = (
        ('Request Details', {
            'fields': ('id', 'user', 'status')
        }),
        ('Financials', {
            'fields': ('amount', 'fee', 'phone_number'),
            'description': "The amount will be debited from the user's Settlement or Personal wallet."
        }),
        ('M-Pesa B2C Tracking', {
            'fields': ('external_reference', 'ledger_entry'),
            'description': "External reference is the Safaricom ConversationID or Receipt Number."
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # --- Custom Display Methods ---

    def id_short(self, obj):
        return f"WDL-{str(obj.id)[:8]}"
    id_short.short_description = "ID"

    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = "User (Acc)"

    @admin.display(description="Net Payout")
    def net_payout(self, obj):
        return obj.amount - obj.fee
