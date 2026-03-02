from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Customer, CustomerStudent
from students.models import Student
from .serializers import CustomerSerializer, CustomerStudentSerializer

class CustomerProfileView(generics.RetrieveAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Customer.objects.get_or_create(user=self.request.user)[0]

class LinkedStudentsView(generics.ListCreateAPIView):
    """
    GET: List all students linked to this Guardian.
    POST: Link a new student using their registration number.
    """
    serializer_class = CustomerStudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show students linked to THIS guardian
        customer = Customer.objects.get(user=self.request.user)
        return CustomerStudent.objects.filter(customer=customer)

    def perform_create(self, serializer):
        customer = Customer.objects.get(user=self.request.user)
        reg_no = serializer.validated_data.pop('reg_no')
        student = Student.objects.get(reg_no=reg_no)

        # Check if already linked
        if CustomerStudent.objects.filter(customer=customer, student=student).exists():
            raise serializer.ValidationError("This student is already linked to your account.")

        serializer.save(customer=customer, student=student)
