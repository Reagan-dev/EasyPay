from django.db import models
from accounts.models import User
import uuid
from students.models import Student

# guardian model which can link to the student who is the child or at the same time customer model for any user in my easypay project innovation.
class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    created_at = models.DateTimeField(auto_now_add=True)

class CustomerStudent(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='customer_students')
    can_view_transactions = models.BooleanField(default=False) 
    can_topup = models.BooleanField(default=True)

    class Meta:
        unique_together = ('customer', 'student')
