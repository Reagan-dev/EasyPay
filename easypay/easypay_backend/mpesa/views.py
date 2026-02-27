from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import MpesaTransaction
from .serializers import MpesaCallbackSerializer

class MpesaCallbackView(APIView):
    """
    The Public Endpoint that Safaricom hits after a user enters their PIN.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MpesaCallbackSerializer(data=request.data)
        
        if serializer.is_valid():
            callback_data = serializer.extract_data()
            
            # Find the pending transaction created during the initial request
            try:
                transaction = MpesaTransaction.objects.get(
                    checkout_request_id=callback_data['checkout_request_id']
                )
                
                # Update with callback data
                for attr, value in callback_data.items():
                    setattr(transaction, attr, value)
                
                # Saving here triggers the 'handle_mpesa_success' signal!
                transaction.save()
                
                return Response({"ResultCode": 0, "ResultDesc": "Success"}, status=status.HTTP_200_OK)
            
            except MpesaTransaction.DoesNotExist:
                # Log this as it might indicate a lost request or a testing error
                return Response({"ResultCode": 1, "ResultDesc": "Internal Error"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
