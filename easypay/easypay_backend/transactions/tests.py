from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

from merchants.models import Business
from wallets.models import Wallet
from payments.models import PaymentIntent
from qrtokens.models import QRToken
from transactions.models import Transaction
from ledger.models import LedgerAccount, SYSTEM_PLATFORM_ID

User = get_user_model()


class TransactionFlowTest(TestCase):

    def setUp(self):

        self.client = APIClient()

        # Merchant user
        self.merchant_user = User.objects.create_user(
            email="merchant@test.com",
            password="testpass123"
        )

        self.business = Business.objects.create(
            user=self.merchant_user,
            name="Campus Cafe"
        )

        # Student user
        self.student_user = User.objects.create_user(
            email="student@test.com",
            password="testpass123"
        )

        self.payer_id = self.student_user.id

        # Wallets
        self.student_wallet = Wallet.objects.create(
            owner_id=self.payer_id,
            type="MEAL",
            balance=Decimal("500.00")
        )

        self.business_wallet = Wallet.objects.create(
            owner_id=self.business.id,
            type="SETTLEMENT",
            balance=Decimal("0.00")
        )

        # Ledger accounts
        LedgerAccount.objects.create(
            owner_id=self.payer_id,
            account_type="STUDENT_MEAL"
        )

        LedgerAccount.objects.create(
            owner_id=self.business.id,
            account_type="BUSINESS_PAYOUT"
        )

        LedgerAccount.objects.create(
            owner_id=SYSTEM_PLATFORM_ID,
            account_type="PLATFORM_REVENUE"
        )

        # Payment Intent
        self.intent = PaymentIntent.objects.create(
            amount=Decimal("100.00"),
            status="PENDING"
        )

        # QR Token
        self.token = QRToken.objects.create(
            token_value="TEST_QR_123",
            amount=Decimal("100.00"),
            status="ACTIVE"
        )

        # Login merchant
        self.client.force_authenticate(user=self.merchant_user)

    def test_process_sale_success(self):
        """
        Merchant processes a sale successfully
        """

        response = self.client.post(
            "/api/transactions/process-sale/",
            {
                "token_value": "TEST_QR_123",
                "intent_id": str(self.intent.id),
                "wallet_type": "MEAL"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        # Transaction created
        self.assertTrue(Transaction.objects.exists())

        txn = Transaction.objects.first()

        self.assertEqual(txn.amount, Decimal("100.00"))
        self.assertEqual(txn.status, "SUCCESS")

    def test_wallet_balance_updated(self):
        """
        Student wallet should decrease after payment
        """

        self.client.post(
            "/api/transactions/process-sale/",
            {
                "token_value": "TEST_QR_123",
                "intent_id": str(self.intent.id),
                "wallet_type": "MEAL"
            },
            format="json"
        )

        self.student_wallet.refresh_from_db()

        self.assertEqual(self.student_wallet.balance, Decimal("400.00"))

    def test_business_receives_payout(self):
        """
        Merchant settlement wallet should receive payout
        """

        self.client.post(
            "/api/transactions/process-sale/",
            {
                "token_value": "TEST_QR_123",
                "intent_id": str(self.intent.id),
                "wallet_type": "MEAL"
            },
            format="json"
        )

        self.business_wallet.refresh_from_db()

        # 100 - 3 fee = 97
        self.assertEqual(self.business_wallet.balance, Decimal("97.00"))

    def test_invalid_qr_token(self):
        """
        Invalid QR token should fail
        """

        response = self.client.post(
            "/api/transactions/process-sale/",
            {
                "token_value": "INVALID",
                "intent_id": str(self.intent.id),
                "wallet_type": "MEAL"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_insufficient_balance(self):
        """
        Payment should fail if wallet balance is insufficient
        """

        self.student_wallet.balance = Decimal("10.00")
        self.student_wallet.save()

        response = self.client.post(
            "/api/transactions/process-sale/",
            {
                "token_value": "TEST_QR_123",
                "intent_id": str(self.intent.id),
                "wallet_type": "MEAL"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_payment_intent_used_once(self):
        """
        Payment intent cannot be reused
        """

        self.client.post(
            "/api/transactions/process-sale/",
            {
                "token_value": "TEST_QR_123",
                "intent_id": str(self.intent.id),
                "wallet_type": "MEAL"
            },
            format="json"
        )

        response = self.client.post(
            "/api/transactions/process-sale/",
            {
                "token_value": "TEST_QR_123",
                "intent_id": str(self.intent.id),
                "wallet_type": "MEAL"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 400)