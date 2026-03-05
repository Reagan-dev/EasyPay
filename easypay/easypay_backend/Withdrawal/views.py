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
from finance.mappings import get_withdrawal_wallet_type_for_user

class WithdrawalRequestView(generics.CreateAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        amount = serializer.validated_data["amount"]

        # 1. Deduct from wallet and create Withdrawal record atomically
        with transaction.atomic():
            w_type = get_withdrawal_wallet_type_for_user(user)

            wallet = Wallet.objects.select_for_update().get(owner_id=user.id, type=w_type)
            if wallet.balance < amount:
                raise ValidationError(f"Insufficient funds in your {w_type} wallet.")
            wallet.balance -= amount
            wallet.save(update_fields=["balance"])

            withdrawal = serializer.save(user=user, status="PROCESSING")

        # 2. Call Safaricom B2C *after* DB commit window to avoid long-running work in transaction
        try:
            res = MpesaService.initiate_b2c_withdrawal(withdrawal)

            if isinstance(res, dict) and res.get("ResponseCode") == "0":
                withdrawal.external_reference = res.get("OriginatorConversationID")
                withdrawal.save(update_fields=["external_reference"])
            else:
                # Mark as FAILED; refund is handled centrally in the Withdrawal signal.
                withdrawal.status = "FAILED"
                withdrawal.save(update_fields=["status"])

                raise ValidationError(
                    {
                        "error": "M-Pesa Gateway rejected the request.",
                        "details": res.get("ResponseDescription", "Connection Timeout")
                        if isinstance(res, dict)
                        else "Gateway Timeout",
                    }
                )

        except Exception as e:
            # Network or other errors: mark FAILED; refund handled once by signal
            withdrawal.status = "FAILED"
            withdrawal.save(update_fields=["status"])
            raise ValidationError(f"M-Pesa Service is currently unavailable: {str(e)}")

class MpesaWithdrawalCallbackView(generics.GenericAPIView):
    permission_classes = [] 

    def post(self, request, *args, **kwargs):
        result = request.data.get("Result", {})
        result_code = result.get("ResultCode")
        conv_id = result.get("OriginatorConversationID")

        try:
            # Make callback idempotent and prevent status regression
            with transaction.atomic():
                withdrawal = Withdrawal.objects.select_for_update().get(
                    external_reference=conv_id
                )

                current_status = withdrawal.status

                # If we've already reached a terminal state, ignore duplicates
                if current_status in ["SUCCESS", "FAILED"]:
                    return Response(
                        {"ResultCode": 0, "ResultDesc": "Already processed"},
                        status=status.HTTP_200_OK,
                    )

                # Map M-Pesa result to our internal status, without regressing SUCCESS
                if result_code == 0:
                    withdrawal.status = "SUCCESS"
                else:
                    withdrawal.status = "FAILED"

                withdrawal.save(update_fields=["status"])
                print(f"DEBUG: Withdrawal {withdrawal.id} finalized as {withdrawal.status}")

        except Withdrawal.DoesNotExist:
            print(f"ERROR: Callback received for unknown reference {conv_id}")
            
        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})