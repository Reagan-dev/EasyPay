from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
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
        # Every User with the BUSINESS role has exactly one Business record
        return Business.objects.get(user=self.request.user)

class BusinessTerminalListView(generics.ListCreateAPIView):
    """
    GET: List all POS terminals for this business.
    POST: Register a new terminal (e.g., a canteen staff tablet).
    """
    serializer_class = BusinessTerminalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Security: Only return terminals for the logged-in merchant
        return BusinessTerminal.objects.filter(business__user=self.request.user)

    def perform_create(self, serializer):
        # Automatically attach the terminal to the logged-in user's business
        business = Business.objects.get(user=self.request.user)
        serializer.save(business=business)