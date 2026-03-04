from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Withdrawal
from .serializers import WithdrawalSerializer
from django.db import transaction
from deposit.services import MpesaService
from wallets.models import Wallet
from rest_framework.exceptions import ValidationError 
from django.db import transaction

class WithdrawalRequestView(generics.CreateAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        with transaction.atomic():
            user = self.request.user
            amount = serializer.validated_data['amount']
            
            # Logic to find wallet type (No migrations needed)
            w_type = "SETTLEMENT" if hasattr(user, 'business') else "POCKET" if hasattr(user, 'student_profile') else "PERSONAL"
            
            # 1. Deduct money immediately
            wallet = Wallet.objects.select_for_update().get(owner_id=user.id, type=w_type)
            wallet.balance -= amount
            wallet.save()

            # 2. Create record
            withdrawal = serializer.save(user=user, status="PROCESSING")

            # 3. Call Safaricom
            try:
                res = MpesaService.initiate_b2c_withdrawal(withdrawal)
                
                # Check if we got a valid dict response and a success code
                if isinstance(res, dict) and res.get("ResponseCode") == "0":
                    withdrawal.external_reference = res.get("ConversationID")
                    withdrawal.save()
                else:
                    # If Safaricom rejected it or timed out, REFUND and FAIL
                    wallet.balance += amount
                    wallet.save()
                    withdrawal.status = "FAILED"
                    withdrawal.save()
                    
                    # Fix the ValidationError call here
                    raise ValidationError({
                        "error": "M-Pesa Gateway rejected the request.",
                        "details": res.get("ResponseDescription", "Connection Timeout") if isinstance(res, dict) else "Gateway Timeout"
                    })

            except Exception as e:
                # Catch-all for network timeouts
                wallet.balance += amount
                wallet.save()
                withdrawal.status = "FAILED"
                withdrawal.save()
                raise ValidationError(f"M-Pesa Service is currently unavailable: {str(e)}")

class MpesaWithdrawalCallbackView(generics.GenericAPIView):
    permission_classes = [] 

    def post(self, request, *args, **kwargs):
        result = request.data.get('Result', {})
        result_code = result.get('ResultCode')
        conv_id = result.get('ConversationID')

        try:
            withdrawal = Withdrawal.objects.get(external_reference=conv_id)
            
            if result_code == 0:
                withdrawal.status = "SUCCESS"
            else:
                withdrawal.status = "FAILED" # This will trigger the Refund Signal
            
            withdrawal.save()
        except Withdrawal.DoesNotExist:
            pass
            
        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})