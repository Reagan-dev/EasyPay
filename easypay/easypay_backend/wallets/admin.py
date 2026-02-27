from django.contrib import admin
from .models import Wallet

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    # 1. Clear visibility of current balances
    list_display = (
        'owner_display', 
        'owner_type', 
        'type', 
        'balance', 
        'is_withdrawable', 
        'created_at'
    )
    
    # 2. Vital filters for financial auditing
    list_filter = ('owner_type', 'type', 'is_withdrawable', 'created_at')
    
    # 3. Search by the UUID (useful for debugging API logs)
    search_fields = ('owner_id', 'id')
    
    # 4. Security: Prevent manual balance editing
    # Changing balance here would cause a "Ledger Mismatch." 
    # Balances should only move via LedgerEntries.
    readonly_fields = ('balance', 'created_at')
    
    # 5. Detail view organization
    fieldsets = (
        ('Ownership Info', {
            'fields': ('owner_type', 'owner_id')
        }),
        ('Wallet Config', {
            'fields': ('type', 'balance', 'is_withdrawable')
        }),
        ('Metadata', {
            'fields': ('created_at',),
        }),
    )

    # --- Custom Display Methods ---

    def owner_display(self, obj):
        """
        Helper to show a hint of who owns this.
        In a more advanced setup, you could use this to link to the User profile.
        """
        return f"{obj.owner_type} ID: {str(obj.owner_id)[:8]}..."
    owner_display.short_description = "Owner"
