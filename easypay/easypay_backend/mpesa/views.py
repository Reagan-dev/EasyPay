from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import MpesaTransaction
from .serializers import MpesaCallbackSerializer

# mpesa/views.py

class MpesaCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MpesaCallbackSerializer(data=request.data)
        if serializer.is_valid():
            callback_data = serializer.extract_data()
            
            try:
                # 1. Fetch the transaction
                transaction = MpesaTransaction.objects.get(
                    checkout_request_id=callback_data['checkout_request_id']
                )
                
                # 2. Update fields (this includes 'status' which the serializer set to SUCCESS/FAILED)
                for attr, value in callback_data.items():
                    if hasattr(transaction, attr):
                        setattr(transaction, attr, value)
                
                # 3. Save triggers the Signal handle_mpesa_success
                transaction.save()
                
                return Response({"ResultCode": 0, "ResultDesc": "Success"}, status=status.HTTP_200_OK)
            
            except MpesaTransaction.DoesNotExist:
                return Response({"ResultCode": 1, "ResultDesc": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
