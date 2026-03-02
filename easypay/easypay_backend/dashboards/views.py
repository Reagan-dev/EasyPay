from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django.utils import timezone
from guardians.models import Customer, CustomerStudent
from wallets.models import Wallet
from transactions.models import Transaction
from qrtokens.models import QRToken
from notifications.models import Notification
from withdrawal.models import Withdrawal
from merchants.models import Business

class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        
        # 1. Wallets & Notifications
        wallets = Wallet.objects.filter(owner_id=user.id)
        meal_bal = wallets.filter(type="MEAL").first().balance
        pocket_bal = wallets.filter(type="POCKET").first().balance
        unread_notifs = Notification.objects.filter(user=user, is_read=False).count()

        # 2. Activity & Security
        today_spend = Transaction.objects.filter(
            payer_id=user.id, status="SUCCESS", created_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        active_qr = QRToken.objects.filter(
            student__user=user, status="ACTIVE", expires_at__gt=timezone.now()
        ).first()

        return Response({
            "full_name": f"{user.first_name} {user.last_name}",
            "meal_balance": meal_bal,
            "pocket_balance": pocket_bal,
            "today_spend": today_spend,
            "unread_notifications_count": unread_notifs,
            "active_qr_token": {"value": active_qr.token_value, "expires": active_qr.expires_at} if active_qr else None,
            "account_status": "ACTIVE"
        })

class MerchantDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not hasattr(user, "business"):
            return Response({"detail": "User is not a merchant."}, status=403)

        biz = user.business
        today = timezone.now().date()

        stats = Transaction.objects.filter(
            business=biz, status="SUCCESS", created_at__date=today
        ).aggregate(total=Sum('amount'))

        settlement_wallet = Wallet.objects.filter(
            owner_type="BUSINESS",
            owner_id=biz.user.id,
            type="SETTLEMENT"
        ).first()

        settlement_bal = settlement_wallet.balance if settlement_wallet else 0

        pending_wd = Withdrawal.objects.filter(user=user, status="PROCESSING").count()
        unread_notifs = Notification.objects.filter(user=user, is_read=False).count()

        return Response({
            "business_name": biz.name,
            "settlement_balance": settlement_bal,
            "today_revenue": stats['total'] or 0,
            "today_tx_count": Transaction.objects.filter(business=biz, created_at__date=today).count(),
            "pending_withdrawals_count": pending_wd,
            "unread_notifications_count": unread_notifs,
            "account_status": "VERIFIED"
        })

class GuardianDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        guardian_profile, _ = Customer.objects.get_or_create(user=user)

        personal_wallet = Wallet.objects.filter(owner_id=user.id, type="PERSONAL").first()
        personal_balance = personal_wallet.balance if personal_wallet else 0

        unread_notifs = Notification.objects.filter(user=user, is_read=False).count()

        children_data = []
        family_total = personal_balance

        for link in guardian_profile.customer_students.all():
            student = link.student

            child_wallets = Wallet.objects.filter(owner_id=student.user.id)
            child_bal = child_wallets.aggregate(total=Sum('balance'))['total'] or 0
            family_total += child_bal

            today_spend = Transaction.objects.filter(
                payer_id=student.user.id,
                created_at__date=today,
                status="SUCCESS"
            ).aggregate(total=Sum('amount'))['total'] or 0

            children_data.append({
                "id": student.id,
                "name": f"{student.user.first_name} {student.user.last_name}",
                "balance": child_bal,
                "today_spend": today_spend
            })

        return Response({
            "guardian_name": f"{user.first_name} {user.last_name}",
            "personal_balance": personal_balance,
            "total_family_value": family_total,
            "unread_notifications_count": unread_notifs,
            "children": children_data,
            "account_status": "ACTIVE"
        })