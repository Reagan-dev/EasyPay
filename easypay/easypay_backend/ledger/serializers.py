from rest_framework import serializers
from .models import LedgerAccount, LedgerEntry

class LedgerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerAccount
        fields = ['id', 'account_type', 'balance']

class LedgerEntrySerializer(serializers.ModelSerializer):
    # Determine the direction relative to the account being viewed
    entry_type = serializers.SerializerMethodField()

    class Meta:
        model = LedgerEntry
        fields = [
            'id', 'amount', 'reference', 'description', 
            'status', 'created_at', 'entry_type'
        ]

    def get_entry_type(self, obj):
        # This is useful for front-end styling (Red for Debit, Green for Credit)
        # We assume the context provides the 'viewing_account'
        viewing_acc = self.context.get('viewing_account')
        if viewing_acc == obj.debit_account:
            return "DEBIT"
        return "CREDIT"