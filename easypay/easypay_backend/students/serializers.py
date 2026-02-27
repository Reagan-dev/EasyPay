from rest_framework import serializers
from .models import Student
from accounts.serializers import UserSerializer

class StudentProfileSerializer(serializers.ModelSerializer):
    # Pulling name, email, and phone from the accounts app
    user_details = UserSerializer(source='user', read_only=True)
    
    # Adding a human-readable created date
    joined_on = serializers.DateTimeField(source='created_at', format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'user_details', 'reg_no', 'joined_on']
        # We make 'user' write_only because we set it automatically in the view
        extra_kwargs = {
            'user': {'write_only': True, 'required': False}
        }

    def validate_reg_no(self, value):
        # Business Rule: Reg numbers should be clean and unique
        value = value.strip().upper()
        if Student.objects.filter(reg_no=value).exists():
            raise serializers.ValidationError("This registration number is already registered.")
        return value