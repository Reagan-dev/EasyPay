from rest_framework import serializers
from .models import Customer, CustomerStudent
from students.models import Student
from students.serializers import StudentProfileSerializer

class CustomerSerializer(serializers.ModelSerializer):
    # Pulling name/phone from the User model
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['id', 'user', 'user_details', 'created_at']
        read_only_fields = ['id']

    def get_user_details(self, obj):
        return {
            "name": f"{obj.user.first_name} {obj.user.last_name}",
            "phone": obj.user.phone
        }

class CustomerStudentSerializer(serializers.ModelSerializer):
    # This allows the parent to see student details (name, reg_no) in the list
    student_details = StudentProfileSerializer(source='student', read_only=True)
    
    # This is for the POST request
    reg_no = serializers.CharField(write_only=True)

    class Meta:
        model = CustomerStudent
        fields = ['id', 'student_details', 'reg_no', 'can_view_transactions', 'can_topup']

    def validate_reg_no(self, value):
        # Verify the student exists before creating the link
        if not Student.objects.filter(reg_no=value.upper()).exists():
            raise serializers.ValidationError("No student found with this registration number.")
        return value.upper()