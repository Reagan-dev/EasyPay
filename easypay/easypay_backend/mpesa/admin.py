from django.contrib import admin
from .models import MpesaTransaction

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    # 1. Quick identification of the transaction
    list_display = (
        'external_txn_id', 
        'phone', 
        'amount', 
        'status', 
        'checkout_request_id', 
        'created_at'
    )
    
    # 2. Filters to isolate failures or specific timeframes
    list_filter = ('status', 'created_at')
    
    # 3. Search by the receipt number or the request IDs
    search_fields = (
        'external_txn_id', 
        'phone', 
        'merchant_request_id', 
        'checkout_request_id'
    )
    
    # 4. Security: All fields should be read-only in Admin
    # We never want an admin to "fake" a successful M-Pesa record manually.
    readonly_fields = [field.name for field in MpesaTransaction._meta.fields]
    
    # 5. Detail view organization
    fieldsets = (
        ('Transaction Summary', {
            'fields': ('external_txn_id', 'status', 'amount', 'phone', 'user_id')
        }),
        ('Safaricom Identifiers', {
            'fields': ('merchant_request_id', 'checkout_request_id'),
            'classes': ('collapse',), # Hide by default to keep it clean
        }),
        ('Audit Log', {
            'fields': ('raw_payload', 'created_at'),
            'description': 'The original JSON data received from Safaricom.'
        }),
    )
