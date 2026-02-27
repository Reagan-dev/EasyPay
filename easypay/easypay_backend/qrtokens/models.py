import uuid
import secrets
from django.db import models
from django.db.models import Q
from django.utils import timezone
from students.models import Student
from guardians.models import Customer

# Create your models here.
class QRToken(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "ACTIVE"),     # Waiting for a scan
        ("USED", "USED"),         # Scanned and used
        ("EXPIRED", "EXPIRED"),   # Time ran out
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='qr_tokens')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='qr_tokens')
    token_value = models.CharField(max_length=255, unique=True, default=secrets.token_urlsafe)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Ensures a student doesn't have 2 active QRs at once
            models.UniqueConstraint(
                fields=["student"],
                condition=Q(status="ACTIVE", student__isnull=False),
                name="one_active_qr_per_student"
            ),
            # Ensures a customer doesn't have 2 active QRs at once
            models.UniqueConstraint(
                fields=["customer"],
                condition=Q(status="ACTIVE", customer__isnull=False),
                name="one_active_qr_per_customer"
            )
        ]

    @property
    def is_valid(self):
        return self.status == "ACTIVE" and self.expires_at > timezone.now()

    def __str__(self):
        owner = self.student if self.student else self.customer
        return f"QR for {owner} - {self.amount} shillings"