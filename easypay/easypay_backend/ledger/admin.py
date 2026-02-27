from django.contrib import admin
from .models import LedgerAccount, LedgerEntry

@admin.register(LedgerAccount)
class LedgerAccountAdmin(admin.ModelAdmin):
    list_display = ('owner_id', 'account_type', 'balance')
    list_filter = ('account_type',)
    search_fields = ('owner_id',)
    readonly_fields = ('balance',) # Balance should only change via LedgerEntry

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    # 1. Shows the "Money Map" in the list view
    list_display = (
        'reference', 
        'debit_account_display', 
        'arrow', 
        'credit_account_display', 
        'amount', 
        'status', 
        'created_at'
    )
    
    # 2. Financial auditing filters
    list_filter = ('status', 'created_at', 'debit_account__account_type')
    search_fields = ('reference', 'description', 'debit_account__owner_id', 'credit_account__owner_id')
    
    # 3. Security: All fields read-only to prevent back-dating or amount tampering
    readonly_fields = [field.name for field in LedgerEntry._meta.fields]
    
    # Custom display methods for better readability
    def debit_account_display(self, obj):
        return f"{obj.debit_account.account_type} ({str(obj.debit_account.owner_id)[:8]})"
    debit_account_display.short_description = "From (Debit)"

    def credit_account_display(self, obj):
        return f"{obj.credit_account.account_type} ({str(obj.credit_account.owner_id)[:8]})"
    credit_account_display.short_description = "To (Credit)"

    def arrow(self, obj):
        return "➡️"
    arrow.short_description = ""