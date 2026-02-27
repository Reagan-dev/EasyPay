from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserRole
from students.models import Student
from merchants.models import Business
from guardians.models import Customer
from wallets.models import Wallet
from ledger.models import LedgerAccount

@receiver(post_save, sender=Student)
def create_student_finances(sender, instance, created, **kwargs):
    if created:
        # create wallets for the student
        Wallet.objects.create(owner_type='STUDENT', owner_id=instance.user.id, type='MEAL')
        Wallet.objects.create(owner_type='STUDENT', owner_id=instance.user.id, type='POCKET')

        # create ledger accounts for the student
        LedgerAccount.objects.create(owner_id=instance.user.id, account_type='STUDENT_MEAL')
        LedgerAccount.objects.create(owner_id=instance.user.id, account_type='STUDENT_POCKET')

@receiver(post_save, sender=Customer)
def setup_customer_finances(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(owner_type='CUSTOMER', owner_id=instance.user.id, type='PERSONAL')
        LedgerAccount.objects.create(owner_id=instance.user.id, account_type='CUSTOMER_MAIN')

@receiver(post_save, sender=Business)
def setup_business_finances(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(owner_type='BUSINESS', owner_id=instance.user.id, type='SETTLEMENT')
        LedgerAccount.objects.create(owner_id=instance.user.id, account_type='BUSINESS_PAYOUT')