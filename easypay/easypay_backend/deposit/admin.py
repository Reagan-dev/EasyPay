from django.contrib import admin
from .models import Deposit

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    # 1. High-level overview for the list view
    list_display = (
        'id', 
        'user_phone', 
        'amount', 
        'target_wallet', 
        'status', 
        'created_at'
    )
    
    # 2. Filters to help find specific issues quickly
    list_filter = ('status', 'target_wallet', 'created_at')
    
    # 3. Search by Phone or ID (Essential for customer support)
    search_fields = ('user__phone', 'id', 'mpesa_reference__mpesa_receipt_number')
    
    # 4. Read-only fields to prevent manual tampering with financial records
    readonly_fields = ('id', 'amount', 'fee', 'ledger_entry', 'mpesa_reference', 'created_at')
    
    # 5. Organization of the detail page
    fieldsets = (
        ('Transaction Info', {
            'fields': ('id', 'user', 'status', 'created_at')
        }),
        ('Financial Details', {
            'fields': ('amount', 'fee', 'target_wallet')
        }),
        ('System Links', {
            'fields': ('mpesa_reference', 'ledger_entry'),
            'description': 'Links to M-Pesa callback and the double-entry ledger.'
        }),
    )

    def user_phone(self, obj):
        return obj.user.phone
    user_phone.short_description = "User Phone"