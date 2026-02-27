from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Withdrawal
from .serializers import WithdrawalSerializer
# from your_mpesa_app.services import MpesaB2C  # Example service

class WithdrawalRequestView(generics.CreateAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # 1. Save as PROCESSING - Money is locked but not yet deducted from Ledger
        withdrawal = serializer.save(
            user=self.request.user,
            status="PROCESSING"
        )

        # 2. Trigger the Real M-Pesa B2C API Call
        # In a real system, use a background task (Celery) so the user doesn't wait
        try:
            # response = MpesaB2C.initiate_transfer(
            #     phone=withdrawal.phone_number,
            #     amount=withdrawal.amount,
            #     reference=str(withdrawal.id)
            # )
            # withdrawal.external_reference = response.get('ConversationID')
            # withdrawal.save()
            pass
        except Exception as e:
            withdrawal.status = "FAILED"
            withdrawal.save()
            raise serializer.ValidationError("M-Pesa service is currently unavailable.")

class MpesaWithdrawalCallbackView(generics.GenericAPIView):
    """
    This is the PUBLIC URL Safaricom hits.
    It DOES NOT require IsAuthenticated because Safaricom calls it.
    """
    permission_classes = [] 

    def post(self, request, *args, **kwargs):
        data = request.data
        # 1. Logic to parse Safaricom's JSON (ResultCode, ResultDesc, etc.)
        # 2. Find the withdrawal using the reference sent back
        # withdrawal = Withdrawal.objects.get(id=data['OriginatorConversationID'])
        
        # 3. IF SUCCESSFUL:
        # withdrawal.status = "SUCCESS"
        # withdrawal.external_reference = data['MpesaReceiptNumber']
        # withdrawal.save()  <-- THIS triggers your signal and moves the money.
        
        return Response({"ResultCode": 0, "ResultDesc": "Success"})
