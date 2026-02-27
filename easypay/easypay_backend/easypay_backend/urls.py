"""
URL configuration for easypay_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Identity & Access
    path('api/accounts/', include('accounts.urls')),
    path('api/dashboards/', include('dashboards.urls')),
    
    # Financial Core
    path('api/deposits/', include('deposit.urls')),
    path('api/ledger/', include('ledger.urls')), # The audit trail
    path('api/transactions/', include('transactions.urls')), # The Engine
    path('api/payments/', include('payments.urls')), # The Merchant-Student Handshake
    path('api/wallets/', include('wallets.urls')),     # The Balances
    path('api/withdrawals/', include('Withdrawal.urls')), # New Payouts
    # Stakeholders
    path('api/guardians/', include('guardians.urls')),
    path('api/merchants/', include('merchants.urls')), # The Merchant/Canteen Endpoints
    path('api/students/', include('students.urls')),   # New student endpoints
    # Third-Party Integrations
    path('api/mpesa/', include('mpesa.urls')), # Public-facing callback
    # Real-time & History Alerts
    path('api/notifications/', include('notifications.urls')),
    path('api/qr/', include('qrtokens.urls')), # Pre-authorized keys
]