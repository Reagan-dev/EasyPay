from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Student
from .serializers import StudentProfileSerializer

class StudentProfileView(generics.RetrieveUpdateAPIView):
    """
    Handles fetching and updating the specific Student profile
    for the currently logged-in user.
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the Student profile linked to the user
        try:
            return Student.objects.get(user=self.request.user)
        except Student.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(
                {"error": "Profile incomplete. Please create your student record."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class StudentCreateView(generics.CreateAPIView):
    """
    POST: Creates the Student record. 
    Used right after a user registers with the 'STUDENT' role.
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Guard: Check if a profile already exists to prevent duplicates
        if Student.objects.filter(user=self.request.user).exists():
            raise serializer.ValidationError("Student profile already exists.")
        
        # Link the profile to the authenticated user automatically
        serializer.save(user=self.request.user)

