from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import QRToken
from .serializers import QRTokenCreateSerializer
from students.models import Student
from guardians.models import Customer
from rest_framework.exceptions import ValidationError

class GenerateQRTokenView(generics.CreateAPIView):
    """
    POST: Generate a new dynamic QR token. 
    Invalidates any existing active token for the user first.
    """
    serializer_class = QRTokenCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        
        # 1. Identify if the user is a Student or a Customer
        student = getattr(user, 'student_profile', None)
        customer = getattr(user, 'customer_profile', None)

        if not student and not customer:
            raise ValidationError("User must be a Student or Customer to generate a QR.")

        # 2. Cleanup: Expire any existing ACTIVE tokens to satisfy DB constraints
        QRToken.objects.filter(
            student=student, 
            customer=customer, 
            status="ACTIVE"
        ).update(status="EXPIRED")

        # 3. Set expiration (e.g., 10 minutes from now)
        expires_at = timezone.now() + timedelta(minutes=1)

        serializer.save(
            student=student,
            customer=customer,
            expires_at=expires_at
        )

class ValidateQRTokenView(generics.RetrieveAPIView):
    """
    GET: Used by the Merchant App to verify a QR code's validity 
    before attempting to process the transaction.
    """
    queryset = QRToken.objects.all()
    lookup_field = 'token_value'
    permission_classes = [IsAuthenticated] # Merchant must be logged in

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_valid:
            return Response({"valid": False, "error": "Token expired or used"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "valid": True,
            "amount": instance.amount,
            "owner": str(instance.student if instance.student else instance.customer)
        })
