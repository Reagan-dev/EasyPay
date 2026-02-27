from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import PaymentIntent
from .serializers import PaymentIntentSerializer
from merchants.models import Business

class CreatePaymentIntentView(generics.CreateAPIView):
    """
    POST: Terminal initiates a payment. 
    Expires any existing pending intent for this terminal first.
    """
    serializer_class = PaymentIntentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        terminal = serializer.validated_data['terminal']
        
        # We need the business instance linked to the user
        try:
            business = Business.objects.get(user=user)
        except Business.DoesNotExist:
            raise serializer.ValidationError("User is not registered as a Business.")

        # ATOMIC STEP: Cleanup and Create
        with transaction.atomic():
            # Invalidate previous pending intent for this terminal to satisfy constraint
            PaymentIntent.objects.filter(
                terminal=terminal,
                status="PENDING"
            ).update(status="EXPIRED")

            # Set expiration to exactly 1 minute (60 seconds)
            expiry = timezone.now() + timedelta(minutes=1)

            serializer.save(
                business=business,
                status="PENDING",
                expires_at=expiry
            )

class PaymentIntentDetailView(generics.RetrieveAPIView):
    """
    GET: Used by the Terminal to poll the status of the payment.
    The terminal will wait until status becomes 'COMPLETED' or 'EXPIRED'.
    """
    queryset = PaymentIntent.objects.all()
    serializer_class = PaymentIntentSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if it should be expired right now
        if instance.status == "PENDING" and not instance.is_active:
            instance.status = "EXPIRED"
            instance.save()
            
        return super().retrieve(request, *args, **kwargs)
