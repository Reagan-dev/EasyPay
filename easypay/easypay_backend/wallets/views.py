from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Wallet
from .serializers import WalletSerializer

class WalletListView(generics.ListAPIView):
    """
    GET: List all wallets belonging to the authenticated user.
    Note: Wallets are automatically created via signals when 
    the user completes their Student/Merchant/Customer profile.
    """
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # We use the User's UUID as the owner_id (as corrected in our signals logic)
        return Wallet.objects.filter(owner_id=self.request.user.id).order_by('-created_at')

class WalletDetailView(generics.RetrieveAPIView):
    """
    GET: Retrieve details for a specific wallet type (e.g., /wallets/MEAL/).
    """
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'type' # Allows the app to query by type name instead of UUID

    def get_queryset(self):
        return Wallet.objects.filter(owner_id=self.request.user.id)