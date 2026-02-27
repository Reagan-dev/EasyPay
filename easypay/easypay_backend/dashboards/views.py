from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django.utils import timezone

from wallets.models import Wallet
from transactions.models import Transaction
from qrtokens.models import QRToken
from notifications.models import Notification
from Withdrawal.models import Withdrawal

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
        biz = user.business
        today = timezone.now().date()

        # 1. Revenue & Wallet
        stats = Transaction.objects.filter(
            business=biz, status="SUCCESS", created_at__date=today
        ).aggregate(total=Sum('amount'), count=Sum('id')) # Count simplified for demo
        
        settlement_bal = Wallet.objects.get(owner_id=biz.id, type="SETTLEMENT").balance
        
        # 2. Operations
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
        guardian_profile = user.customer_profile
        today = timezone.now().date()

        # 1. Personal Finances (Purchases/Withdrawals)
        personal_wallet = Wallet.objects.get(owner_id=user.id, type="PERSONAL")
        unread_notifs = Notification.objects.filter(user=user, is_read=False).count()

        # 2. Children Monitoring
        children_data = []
        family_total = personal_wallet.balance
        
        for child in guardian_profile.students.all():
            child_wallets = Wallet.objects.filter(owner_id=child.user.id)
            child_bal = child_wallets.aggregate(Sum('balance'))['balance__sum'] or 0
            family_total += child_bal
            
            children_data.append({
                "id": child.id,
                "name": f"{child.first_name} {child.last_name}",
                "balance": child_bal,
                "today_spend": Transaction.objects.filter(
                    payer_id=child.user.id, created_at__date=today
                ).aggregate(Sum('amount'))['amount__sum'] or 0
            })

        return Response({
            "guardian_name": user.first_name,
            "personal_balance": personal_wallet.balance,
            "total_family_value": family_total,
            "unread_notifications_count": unread_notifs,
            "children": children_data,
            "account_status": "ACTIVE"
        })