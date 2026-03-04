from typing import Literal


WalletType = Literal["MEAL", "POCKET", "PERSONAL", "SETTLEMENT", "REVENUE"]


def get_withdrawal_wallet_type_for_user(user) -> WalletType:
    """
    Centralised mapping of user role → wallet type for withdrawals.
    """
    if hasattr(user, "business"):
        return "SETTLEMENT"
    if hasattr(user, "student_profile"):
        return "POCKET"
    return "PERSONAL"


def get_ledger_account_type_for_wallet(wallet_type: WalletType) -> str:
    """
    Centralised mapping of wallet type → ledger account_type.
    """
    mapping = {
        "MEAL": "STUDENT_MEAL",
        "POCKET": "STUDENT_POCKET",
        "PERSONAL": "CUSTOMER_MAIN",
        "SETTLEMENT": "BUSINESS_PAYOUT",
        "REVENUE": "PLATFORM_REVENUE",
    }
    return mapping.get(wallet_type, "CUSTOMER_MAIN")

