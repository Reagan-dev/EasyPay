from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import LedgerAccount, LedgerEntry
from .serializers import LedgerAccountSerializer, LedgerEntrySerializer

class LedgerAccountSummaryView(generics.ListAPIView):
    """
    GET: Returns all ledger accounts owned by the user (Meal, Pocket, etc.)
    """
    serializer_class = LedgerAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LedgerAccount.objects.filter(owner_id=self.request.user.id)

class LedgerStatementView(generics.ListAPIView):
    """
    GET: Returns a history of all money movements for a specific account.
    Example URL: /ledger/statement/STUDENT_MEAL/
    """
    serializer_class = LedgerEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        account_type = self.kwargs['account_type']
        try:
            # Find the specific account owned by the user
            account = LedgerAccount.objects.get(
                owner_id=self.request.user.id, 
                account_type=account_type
            )
            # Find entries where this account was either the sender or receiver
            return LedgerEntry.objects.filter(
                Q(debit_account=account) | Q(credit_account=account)
            ).order_by('-created_at')
        except LedgerAccount.DoesNotExist:
            return LedgerEntry.objects.none()

    def get_serializer_context(self):
        # Pass the account being viewed to the serializer to determine Debit/Credit
        context = super().get_serializer_context()
        try:
            account = LedgerAccount.objects.get(
                owner_id=self.request.user.id, 
                account_type=self.kwargs['account_type']
            )
            context['viewing_account'] = account
        except LedgerAccount.DoesNotExist:
            context['viewing_account'] = None
        return context