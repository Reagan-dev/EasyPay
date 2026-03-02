from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Business, BusinessTerminal
from .serializers import BusinessProfileSerializer, BusinessTerminalSerializer

class BusinessProfileView(generics.RetrieveUpdateAPIView):
    """
    GET: View Business details (Till Number, Terminals, etc.)
    PATCH: Update Business Name or Category
    """
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Auto-create profile if it doesn't exist (prevents 500s)
        business, _ = Business.objects.get_or_create(user=self.request.user)
        return business

class BusinessTerminalListView(generics.ListCreateAPIView):
    """
    GET: List all POS terminals for this business.
    POST: Register a new terminal (e.g., a canteen staff tablet).
    """
    serializer_class = BusinessTerminalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BusinessTerminal.objects.filter(business__user=self.request.user)

    def perform_create(self, serializer):
        # Ensure business exists
        business, _ = Business.objects.get_or_create(user=self.request.user)
        serializer.save(business=business)