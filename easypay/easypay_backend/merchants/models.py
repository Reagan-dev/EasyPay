from django.db import models
from accounts.models import User
import uuid

# this contains the business models holding business information in my easypay project innovation.
class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business')
    name = models.CharField(max_length=255)
    category_code = models.CharField(max_length=50)
    mpesa_till_number = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BusinessTerminal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='terminals')
    device_id = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)
    is_online = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)