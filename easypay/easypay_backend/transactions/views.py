from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction
from .models import Transaction
from .serializers import SaleExecutionSerializer
from merchants.models import Business

class ProcessSaleView(generics.CreateAPIView):
    """
    POST: Final handshake. Matches scanned QRToken with terminal PaymentIntent.
    Triggers Ledger and Wallet updates via signals.
    """
    serializer_class = SaleExecutionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        token = serializer.validated_data["token_object"]
        intent = serializer.validated_data["intent_object"]
        payer_id = serializer.validated_data["payer_user_id"]
        wallet_type = serializer.validated_data["wallet_type"]

        # Ensure the user executing the sale is the business owner
        try:
            business = Business.objects.get(user=self.request.user)
        except Business.DoesNotExist:
            raise serializer.ValidationError("Unauthorized: Only business accounts can process sales.")

        # Execute all status changes and record creation in one atomic block
        with db_transaction.atomic():
            # Lock the intent and token rows to make this operation idempotent
            intent = intent.__class__.objects.select_for_update().get(pk=intent.pk)
            token = token.__class__.objects.select_for_update().get(pk=token.pk)

            # If another request already completed this intent or used this token, abort.
            if not intent.is_active or not token.is_valid:
                raise serializer.ValidationError(
                    "This payment request has already been processed."
                )

            # 1. Create Transaction (This triggers your handle_transaction_success signal)
            transaction_record = serializer.save(
                business=business,
                payer_id=payer_id,
                payer_type="STUDENT" if token.student else "CUSTOMER",
                amount=intent.amount,
                wallet_type=wallet_type,
                payment_intent=intent,
                status="SUCCESS",
            )

            # 2. Burn the QR Token so it can't be reused
            token.status = "USED"
            token.save(update_fields=["status"])

            # 3. Finalize the Payment Intent for the Terminal
            intent.status = "COMPLETED"
            intent.payer_id = payer_id
            intent.payer_type = transaction_record.payer_type
            intent.save(update_fields=["status", "payer_id", "payer_type"])

    def create(self, request, *args, **kwargs):
        # Override create to return a clean receipt-style response
        response = super().create(request, *args, **kwargs)
        return Response({
            "status": "success",
            "message": "Payment processed successfully",
            "receipt_no": f"TXN-{response.data['id'][:8].upper()}"
        }, status=status.HTTP_201_CREATED)

class MerchantActivityView(generics.ListAPIView):
    """
    GET: View recent sales history for the logged-in merchant.
    """
    serializer_class = SaleExecutionSerializer 
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            business__user=self.request.user
        ).order_by('-created_at')