from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # 1. High-level financial overview
    list_display = (
        'id_short', 
        'payer_info', 
        'business', 
        'wallet_type', 
        'amount', 
        'platform_fee', 
        'payout', 
        'status', 
        'created_at'
    )
    
    # 2. Filters for daily reconciliation
    list_filter = ('status', 'wallet_type', 'payer_type', 'created_at', 'business')
    
    # 3. Search by ID, Payer ID, or Business Name
    search_fields = ('id', 'payer_id', 'business__name')
    
    # 4. Read-only to protect the integrity of financial records
    readonly_fields = [field.name for field in Transaction._meta.fields] + ['payout']
    
    # 5. Detail view organization
    fieldsets = (
        ('Transaction Identity', {
            'fields': ('id', 'status', 'created_at')
        }),
        ('Parties Involved', {
            'fields': ('payer_type', 'payer_id', 'business')
        }),
        ('Financial Breakdown', {
            'fields': ('amount', 'platform_fee', 'payout', 'wallet_type'),
            'description': "Note: The 'Payout' is the amount sent to the Merchant's Settlement wallet."
        }),
        ('System Links', {
            'fields': ('payment_intent', 'ledger_entry'),
            'classes': ('collapse',),
        }),
    )

    # --- Custom Display Methods ---

    def id_short(self, obj):
        return f"TXN-{str(obj.id)[:8]}"
    id_short.short_description = "Transaction ID"

    def payer_info(self, obj):
        return f"{obj.payer_type} ({str(obj.payer_id)[:8]})"
    payer_info.short_description = "Payer"

    @admin.display(description="Merchant Payout")
    def payout(self, obj):
        return f"KES {obj.merchant_payout}"
