from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Deposit
from .serializers import DepositRequestSerializer
from .services import MpesaService
 

class DepositInitiateView(generics.CreateAPIView):
    """
    POST: Initiates a top-up via M-Pesa STK Push.
    """
    serializer_class = DepositRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
    # Trigger the service which handles the M-Pesa handshake
        MpesaService.initiate_stk_push(
          user=self.request.user,
          amount=serializer.validated_data['amount'],
          phone=serializer.validated_data['phone_number'],
          target_wallet=serializer.validated_data['target_wallet']
    )

class DepositHistoryView(generics.ListAPIView):
    """
    GET: Returns all deposits made by the user.
    """
    serializer_class = DepositRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Deposit.objects.filter(user=self.request.user).order_by('-created_at')