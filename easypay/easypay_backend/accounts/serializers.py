from rest_framework import serializers
from .models import User, UserRole, Role

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['role']

class UserSerializer(serializers.ModelSerializer):
    roles = UserRoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'first_name', 'last_name', 'roles']

class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Role.choices, write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'phone', 'first_name', 'last_name', 'password', 'role']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value

    def create(self, validated_data):
        role_choice = validated_data.pop('role')
        # customUserManager hashes the password via create_user
        user = User.objects.create_user(**validated_data)
        UserRole.objects.create(user=user, role=role_choice)
        return user