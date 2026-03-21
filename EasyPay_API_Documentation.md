# 🧾 EasyPay API Documentation

## 1. 📌 Project Overview

EasyPay is a closed-loop digital payment and financial management platform designed to enable fast, secure, and intelligent transactions within controlled ecosystems. The platform connects students, guardians or all customers, merchants which are businesses, and administrators through a unified system powered by M-Pesa integration and QR-based payments.

At its core, EasyPay replaces slow, manual mobile money interactions with a real-time, ledger-driven infrastructure that supports instant payments, transaction tracking, and programmable financial controls.

-Purpose

The primary goal of EasyPay is to:

Eliminate transaction delays caused by traditional mobile money workflows

Provide transparent and traceable financial records through a centralized ledger

Enable controlled spending using digital wallets

Improve operational efficiency for merchants and institutions

Reduce transaction expences

-How It Works (High-Level)

EasyPay operates on a two-layer financial architecture:

External Layer (M-Pesa Integration via Safaricom Daraja):

Handles deposits (STK Push), withdrawals (B2C)

Acts as the bridge between real-world money and the platform

Internal Layer (Ledger System):

Maintains users balances

Processes transactions instantly (sub-second)

Records all financial activities with full audit trails

- Key Concept: Closed-Loop Payments

Unlike traditional payment systems where every transaction goes through external providers, EasyPay uses a closed-loop model:

Funds are first deposited into the platform

All day-to-day transactions occur internally via the ledger

External APIs are only used for entry (top-up) and exit (withdrawal)

This approach ensures:

⚡ Faster transactions

💰 Lower operational costs

📊 Better financial control and visibility

🚀 Core Capabilities

QR-Based Payments:
Users make payments by presenting a secure, time-sensitive QR code, enabling fast “scan-and-go” transactions.

Smart Wallets (Programmable Money):
Funds can be categorized (e.g., meals, personal).

Real-Time Ledger:
Every transaction is processed atomically, updating balances instantly while maintaining a complete transaction history.

Transaction Tracking & Transparency:
Users can view detailed histories of all transactions, ensuring accountability and financial awareness.

Multi-User Ecosystem:
Supports different roles:

Students (end users)

customers (end users)

businesses (service providers)

Admins (system managers)

- System Vision

EasyPay goes beyond being a simple wallet by acting as a:

Behavioral financial system that optimizes speed, enforces smart spending, and provides real-time financial visibility.

It is designed to scale while maintaining data isolation, transaction accuracy, and system reliability.

### Key Features:
- **Multi-role Authentication**: Students, Guardians (Parents), Merchants, and Administrators
- **Digital Wallets**: Multiple wallet types (MEAL, POCKET, PERSONAL, SETTLEMENT)
- **M-Pesa Integration**: STK push deposits and B2C withdrawals
- **QR Token System**: Dynamic QR codes for contactless payments
- **Payment Processing**: Merchant-student transaction handling
- **Financial Ledger**: Complete audit trail and account statements
- **Real-time Notifications**: In-app notification system
- **Role-based Dashboards**: Tailored insights for each user type

### Tech Stack:
- **Backend**: Django REST Framework
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: PostgreSQL with UUID primary keys
- **Payment Gateway**: M-Pesa API Integration
- **Architecture**: RESTful API with role-based access control

---

## 2. 🔐 Authentication

EasyPay uses JWT (JSON Web Tokens) for authentication. The system issues two tokens upon login:
- **Access Token**: Short-lived token for API requests (expires in minutes)
- **Refresh Token**: Long-lived token for obtaining new access tokens

### Login Endpoint

**Method:** POST
**URL:** `/api/accounts/login/`

### Description:
Authenticates a user with email and password, returning JWT tokens for subsequent API requests.

### Request:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### Response:
```json
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "roles": [
      {
        "role": "STUDENT"
      }
    ]
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### Status Codes:
- **200 OK** → Authentication successful
- **401 Unauthorized** → Invalid credentials

### Authentication:
No authentication required

### Refresh Token Endpoint

**Method:** POST
**URL:** `/api/accounts/token/refresh/`

### Description:
Exchanges a valid refresh token for a new access token without requiring full re-authentication.

### Request:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Status Codes:
- **200 OK** → Token refreshed successfully
- **401 Unauthorized** → Invalid or expired refresh token

### Authentication:
No authentication required

---

## 3. 📡 API Endpoints

### Authentication

#### Register

**Method:** POST
**URL:** `/api/accounts/register/`

### Description:
Registers a new user in the system with a specific role. The role determines the user's permissions and available features.

### Request:
```json
{
  "email": "user@example.com",
  "phone": "0712345678",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "role": "STUDENT"
}
```

### Response:
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "phone": "0712345678",
  "first_name": "John",
  "last_name": "Doe",
  "roles": [
    {
      "role": "STUDENT"
    }
  ]
}
```

### Status Codes:
- **201 Created** → User registered successfully
- **400 Bad Request** → Validation error or duplicate data

### Authentication:
No authentication required

#### Logout

**Method:** POST
**URL:** `/api/accounts/logout/`

### Description:
Blacklists the provided refresh token, effectively logging the user out and invalidating the token.

### Request:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Response:
```json
{
  "message": "Successfully logged out"
}
```

### Status Codes:
- **205 Reset Content** → Logout successful
- **400 Bad Request** → Invalid token
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Get Current User

**Method:** GET
**URL:** `/api/accounts/me/`

### Description:
Returns the authenticated user's profile information including their assigned roles.

### Response:
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "phone": "0712345678",
  "first_name": "John",
  "last_name": "Doe",
  "roles": [
    {
      "role": "STUDENT"
    }
  ]
}
```

### Status Codes:
- **200 OK** → Profile retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

### Students

#### Setup Student Profile

**Method:** POST
**URL:** `/api/students/setup/`

### Description:
Creates a student profile and links it to the authenticated user account using a registration number.

### Request:
```json
{
  "reg_no": "STU/2024/001"
}
```

### Response:
```json
{
  "id": "uuid-string",
  "user": "uuid-string",
  "reg_no": "STU/2024/001",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **201 Created** → Student profile created
- **400 Bad Request** → Validation error
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Get Student Profile

**Method:** GET
**URL:** `/api/students/me/`

### Description:
Returns the student profile for the authenticated user.

### Response:
```json
{
  "id": "uuid-string",
  "user": "uuid-string",
  "reg_no": "STU/2024/001",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **200 OK** → Profile retrieved successfully
- **401 Unauthorized** → Authentication required
- **404 Not Found** → Student profile not found

### Authentication:
Required (Bearer token)

#### Update Student Profile

**Method:** PATCH
**URL:** `/api/students/me/`

### Description:
Partially updates the student profile. All fields are optional.

### Request:
```json
{
  "reg_no": "STU/2024/002"
}
```

### Response:
```json
{
  "id": "uuid-string",
  "user": "uuid-string",
  "reg_no": "STU/2024/002",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T11:00:00Z"
}
```

### Status Codes:
- **200 OK** → Profile updated successfully
- **400 Bad Request** → Validation error
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

### Merchants

#### Get Business Profile

**Method:** GET
**URL:** `/api/merchants/profile/`

### Description:
Returns the merchant's business profile including name, category, till number, and all registered terminals.

### Response:
```json
{
  "id": "uuid-string",
  "user": "uuid-string",
  "name": "My Canteen",
  "category_code": "FOOD",
  "mpesa_till_number": "123456",
  "is_active": true,
  "terminals": [
    {
      "id": "uuid-string",
      "device_id": "DEVICE-001",
      "location": "Main Cafeteria - Counter 1",
      "is_online": true
    }
  ]
}
```

### Status Codes:
- **200 OK** → Profile retrieved successfully
- **401 Unauthorized** → Authentication required
- **404 Not Found** → Business profile not found

### Authentication:
Required (Bearer token)

#### Update Business Profile

**Method:** PATCH
**URL:** `/api/merchants/profile/`

### Description:
Partially updates the business profile. Category must be `FOOD` or `OTHERS`.

### Request:
```json
{
  "name": "My Canteen",
  "category_code": "FOOD"
}
```

### Response:
```json
{
  "id": "uuid-string",
  "name": "My Canteen",
  "category_code": "FOOD",
  "mpesa_till_number": "123456",
  "is_active": true
}
```

### Status Codes:
- **200 OK** → Profile updated successfully
- **400 Bad Request** → Validation error
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### List Terminals

**Method:** GET
**URL:** `/api/merchants/terminals/`

### Description:
Returns all POS terminals registered under the authenticated merchant's business.

### Response:
```json
[
  {
    "id": "uuid-string",
    "business": "uuid-string",
    "device_id": "DEVICE-001",
    "location": "Main Cafeteria - Counter 1",
    "is_online": true,
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### Status Codes:
- **200 OK** → Terminals retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Register Terminal

**Method:** POST
**URL:** `/api/merchants/terminals/`

### Description:
Registers a new POS terminal for the authenticated merchant's business.

### Request:
```json
{
  "device_id": "DEVICE-001",
  "location": "Main Cafeteria - Counter 1"
}
```

### Response:
```json
{
  "id": "uuid-string",
  "business": "uuid-string",
  "device_id": "DEVICE-001",
  "location": "Main Cafeteria - Counter 1",
  "is_online": true,
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **201 Created** → Terminal registered successfully
- **400 Bad Request** → Validation error
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

### Guardians

#### Get Guardian Profile

**Method:** GET
**URL:** `/api/guardians/profile/`

### Description:
Returns the guardian's profile including their name and phone number.

### Response:
```json
{
  "id": "uuid-string",
  "user": "uuid-string",
  "phone": "0712345678",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **200 OK** → Profile retrieved successfully
- **401 Unauthorized** → Authentication required
- **404 Not Found** → Guardian profile not found

### Authentication:
Required (Bearer token)

#### List Linked Students

**Method:** GET
**URL:** `/api/guardians/students/`

### Description:
Returns all students linked to the authenticated guardian's account.

### Response:
```json
[
  {
    "id": "uuid-string",
    "reg_no": "STU/2024/001",
    "first_name": "Student",
    "last_name": "Name",
    "can_view_transactions": true,
    "can_topup": true
  }
]
```

### Status Codes:
- **200 OK** → Students retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Link a Student

**Method:** POST
**URL:** `/api/guardians/students/`

### Description:
Links a student to the guardian's account using the student's registration number. The student must already exist in the system.

### Request:
```json
{
  "reg_no": "STU/2024/001"
}
```

### Response:
```json
{
  "id": "uuid-string",
  "guardian": "uuid-string",
  "student": "uuid-string",
  "can_view_transactions": true,
  "can_topup": true,
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **201 Created** → Student linked successfully
- **400 Bad Request** → Validation error or student not found
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

### Wallets

#### List All Wallets

**Method:** GET
**URL:** `/api/wallets/`

### Description:
Returns all wallets belonging to the authenticated user with their current balances.

### Response:
```json
[
  {
    "id": "uuid-string",
    "owner_type": "STUDENT",
    "owner_id": "uuid-string",
    "type": "MEAL",
    "balance": 1500.00,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  },
  {
    "id": "uuid-string",
    "owner_type": "STUDENT",
    "owner_id": "uuid-string",
    "type": "POCKET",
    "balance": 500.00,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
]
```

### Status Codes:
- **200 OK** → Wallets retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Get Wallet by Type

**Method:** GET
**URL:** `/api/wallets/{wallet_type}/`

### Description:
Returns details for a specific wallet type. Replace `MEAL` with `POCKET`, `PERSONAL`, or `SETTLEMENT` as needed.

### Response:
```json
{
  "id": "uuid-string",
  "owner_type": "STUDENT",
  "owner_id": "uuid-string",
  "type": "MEAL",
  "balance": 1500.00,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **200 OK** → Wallet retrieved successfully
- **401 Unauthorized** → Authentication required
- **404 Not Found** → Wallet type not found

### Authentication:
Required (Bearer token)

### Payments

#### Create Payment Intent

**Method:** POST
**URL:** `/api/payments/intent/create/`

### Description:
Creates a payment intent from a POS terminal. The intent expires in 1 minute. Terminal must be a UUID of registered terminal.

### Request:
```json
{
  "terminal": "uuid-string",
  "amount": 150.00
}
```

### Response:
```json
{
  "id": "uuid-string",
  "terminal": "uuid-string",
  "amount": 150.00,
  "status": "PENDING",
  "expires_at": "2024-01-01T10:01:00Z",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **201 Created** → Payment intent created
- **400 Bad Request** → Validation error
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Get Payment Intent Status

**Method:** GET
**URL:** `/api/payments/intent/{uuid}/`

### Description:
Polls the status of a payment intent. Used by terminal to check if student has completed payment.

### Response:
```json
{
  "id": "uuid-string",
  "terminal": "uuid-string",
  "amount": 150.00,
  "status": "COMPLETED",
  "student": "uuid-string",
  "completed_at": "2024-01-01T10:00:30Z",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **200 OK** → Status retrieved successfully
- **401 Unauthorized** → Authentication required
- **404 Not Found** → Payment intent not found

### Authentication:
Required (Bearer token)

### QR Tokens

#### Generate QR Token

**Method:** POST
**URL:** `/api/qr/generate/`

### Description:
Generates a new dynamic QR token for the authenticated student or guardian. Invalidates any existing active token. Token expires in 1 minute.

### Request:
```json
{
  "amount": 150.00,
  "wallet_type": "MEAL"
}
```

### Response:
```json
{
  "token": "ABC123XYZ789",
  "amount": 150.00,
  "wallet_type": "MEAL",
  "owner": "uuid-string",
  "expires_at": "2024-01-01T10:01:00Z",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **201 Created** → QR token generated
- **400 Bad Request** → Validation error
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Validate QR Token

**Method:** GET
**URL:** `/api/qr/validate/{token_value}/`

### Description:
Used by merchant app to verify a scanned QR code before processing a transaction. Returns validity status, amount, and owner.

### Response:
```json
{
  "valid": true,
  "token": "ABC123XYZ789",
  "amount": 150.00,
  "wallet_type": "MEAL",
  "owner": {
    "id": "uuid-string",
    "name": "John Doe",
    "type": "STUDENT"
  },
  "expires_at": "2024-01-01T10:01:00Z"
}
```

### Status Codes:
- **200 OK** → Token validated successfully
- **404 Not Found** → Token not found or expired

### Authentication:
No authentication required (public endpoint)

### Transactions

#### Process Sale

**Method:** POST
**URL:** `/api/transactions/process-sale/`

### Description:
Executes a payment by matching a student's QR token with a merchant's payment intent. Validates amounts match, checks wallet balance, and processes the transfer.

### Request:
```json
{
  "token_value": "ABC123XYZ789",
  "intent_id": "uuid-string",
  "wallet_type": "MEAL"
}
```

### Response:
```json
{
  "id": "uuid-string",
  "from_wallet": "uuid-string",
  "to_wallet": "uuid-string",
  "amount": 150.00,
  "status": "COMPLETED",
  "reference": "TXN123456789",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **201 Created** → Transaction processed successfully
- **400 Bad Request** → Validation error or insufficient funds
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Transaction History

**Method:** GET
**URL:** `/api/transactions/history/`

### Description:
Returns all transactions for the authenticated merchant's business.

### Response:
```json
[
  {
    "id": "uuid-string",
    "from_wallet": "uuid-string",
    "to_wallet": "uuid-string",
    "amount": 150.00,
    "status": "COMPLETED",
    "reference": "TXN123456789",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### Status Codes:
- **200 OK** → Transactions retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

### Deposits

#### Initiate Deposit

**Method:** POST
**URL:** `/api/deposits/initiate/`

### Description:
Initiates an M-Pesa STK push to top up a wallet. Minimum amount is KES 10. Phone must be in format `0XXXXXXXXX`.

### Request:
```json
{
  "amount": 500,
  "target_wallet": "MEAL",
  "phone_number": "0712345678"
}
```

### Response:
```json
{
  "id": "uuid-string",
  "user": "uuid-string",
  "amount": 500,
  "target_wallet": "MEAL",
  "phone_number": "0712345678",
  "status": "PENDING",
  "mpesa_request_id": "ws_CO_191220191020363925",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **201 Created** → Deposit initiated
- **400 Bad Request** → Validation error
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Deposit History

**Method:** GET
**URL:** `/api/deposits/history/`

### Description:
Returns all deposits made by the authenticated user.

### Response:
```json
[
  {
    "id": "uuid-string",
    "user": "uuid-string",
    "amount": 500,
    "target_wallet": "MEAL",
    "status": "SUCCESS",
    "mpesa_receipt": "NLJ7RT61SV",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### Status Codes:
- **200 OK** → Deposits retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

### Withdrawals

#### Request Withdrawal

**Method:** POST
**URL:** `/api/withdrawals/request/`

### Description:
Initiates an M-Pesa B2C transfer. Wallet source is determined by role: merchants use `SETTLEMENT`, students use `POCKET`, guardians use `PERSONAL`.

### Request:
```json
{
  "amount": 200,
  "phone_number": "0712345678"
}
```

### Response:
```json
{
  "id": "uuid-string",
  "user": "uuid-string",
  "amount": 200,
  "phone_number": "0712345678",
  "status": "PENDING",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Status Codes:
- **201 Created** → Withdrawal requested
- **400 Bad Request** → Validation error or insufficient funds
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### M-Pesa Withdrawal Callback

**Method:** POST
**URL:** `/api/withdrawals/callback/`

### Description:
Public endpoint called by Safaricom to deliver B2C transaction results. Not for direct use — this is called automatically by M-Pesa.

### Request:
```json
{
  "Result": {
    "ResultCode": 0,
    "ResultDesc": "The service request is processed successfully.",
    "TransactionID": "NLJ7RT61SV",
    "ResultParameters": {
      "ResultParameter": [
        {
          "Key": "TransactionAmount",
          "Value": 200
        },
        {
          "Key": "TransactionReceipt",
          "Value": "NLJ7RT61SV"
        },
        {
          "Key": "ReceiverPartyPublicName",
          "Value": "254712345678 - John Doe"
        }
      ]
    }
  }
}
```

### Response:
```json
{
  "status": "success",
  "message": "Callback processed"
}
```

### Status Codes:
- **200 OK** → Callback processed successfully

### Authentication:
No authentication required (public webhook)

### M-Pesa

#### STK Push Callback

**Method:** POST
**URL:** `/api/mpesa/callback/`

### Description:
Public endpoint called by Safaricom to deliver STK push transaction results. Not for direct use — this is called automatically by M-Pesa.

### Request:
```json
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "29115-34620561-1",
      "CheckoutRequestID": "ws_CO_191220191020363925",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {
            "Name": "Amount",
            "Value": 500
          },
          {
            "Name": "MpesaReceiptNumber",
            "Value": "NLJ7RT61SV"
          },
          {
            "Name": "PhoneNumber",
            "Value": 254712345678
          }
        ]
      }
    }
  }
}
```

### Response:
```json
{
  "status": "success",
  "message": "Callback processed"
}
```

### Status Codes:
- **200 OK** → Callback processed successfully

### Authentication:
No authentication required (public webhook)

### Notifications

#### List Notifications

**Method:** GET
**URL:** `/api/notifications/`

### Description:
Returns all notifications for the authenticated user, newest first.

### Response:
```json
[
  {
    "id": "uuid-string",
    "user": "uuid-string",
    "title": "Payment Received",
    "message": "You received KES 150.00 from My Canteen",
    "type": "PAYMENT",
    "read": false,
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### Status Codes:
- **200 OK** → Notifications retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Mark Notification as Read

**Method:** PATCH
**URL:** `/api/notifications/{uuid}/read/`

### Description:
Marks a specific notification as read.

### Response:
```json
{
  "id": "uuid-string",
  "read": true,
  "read_at": "2024-01-01T10:30:00Z"
}
```

### Status Codes:
- **200 OK** → Notification marked as read
- **401 Unauthorized** → Authentication required
- **404 Not Found** → Notification not found

### Authentication:
Required (Bearer token)

#### Mark All Notifications as Read

**Method:** POST
**URL:** `/api/notifications/read-all/`

### Description:
Marks all unread notifications as read for the authenticated user.

### Response:
```json
{
  "message": "All notifications marked as read",
  "count": 5
}
```

### Status Codes:
- **200 OK** → All notifications marked as read
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

### Dashboards

#### Student Dashboard

**Method:** GET
**URL:** `/api/dashboards/student/`

### Description:
Returns student dashboard data: meal & pocket balances, today's spend, unread notifications count, and active QR token if any.

### Response:
```json
{
  "user": {
    "name": "John Doe",
    "reg_no": "STU/2024/001"
  },
  "wallets": {
    "meal_balance": 1500.00,
    "pocket_balance": 500.00
  },
  "today_spend": 250.00,
  "unread_notifications": 3,
  "active_qr_token": {
    "token": "ABC123XYZ789",
    "amount": 150.00,
    "expires_at": "2024-01-01T10:01:00Z"
  }
}
```

### Status Codes:
- **200 OK** → Dashboard data retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Merchant Dashboard

**Method:** GET
**URL:** `/api/dashboards/merchant/`

### Description:
Returns merchant dashboard data: business name, settlement balance, today's revenue, transaction count, pending withdrawals, and unread notifications.

### Response:
```json
{
  "business": {
    "name": "My Canteen",
    "category": "FOOD"
  },
  "settlement_balance": 5000.00,
  "today_revenue": 2500.00,
  "today_transactions": 25,
  "pending_withdrawals": 1,
  "unread_notifications": 2
}
```

### Status Codes:
- **200 OK** → Dashboard data retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Guardian Dashboard

**Method:** GET
**URL:** `/api/dashboards/guardian/`

### Description:
Returns guardian dashboard data: personal balance, total family value, unread notifications, and a summary of each linked child's balance and today's spend.

### Response:
```json
{
  "personal_balance": 2000.00,
  "total_family_value": 4500.00,
  "unread_notifications": 1,
  "children": [
    {
      "name": "John Doe",
      "reg_no": "STU/2024/001",
      "meal_balance": 1500.00,
      "pocket_balance": 500.00,
      "today_spend": 250.00
    }
  ]
}
```

### Status Codes:
- **200 OK** → Dashboard data retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

### Ledger

#### Account Summary

**Method:** GET
**URL:** `/api/ledger/accounts/`

### Description:
Returns all ledger accounts owned by the authenticated user (e.g. Meal, Pocket) with their current balances.

### Response:
```json
[
  {
    "id": "uuid-string",
    "owner_id": "uuid-string",
    "account_type": "STUDENT_MEAL",
    "balance": 1500.00,
    "created_at": "2024-01-01T10:00:00Z"
  },
  {
    "id": "uuid-string",
    "owner_id": "uuid-string",
    "account_type": "STUDENT_POCKET",
    "balance": 500.00,
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### Status Codes:
- **200 OK** → Accounts retrieved successfully
- **401 Unauthorized** → Authentication required

### Authentication:
Required (Bearer token)

#### Account Statement

**Method:** GET
**URL:** `/api/ledger/statement/{account_type}/`

### Description:
Returns a full history of all money movements (debits and credits) for a specific ledger account type.

### Response:
```json
[
  {
    "id": "uuid-string",
    "debit_account": "uuid-string",
    "credit_account": "uuid-string",
    "amount": 150.00,
    "reference": "TXN123456789",
    "description": "Payment at My Canteen",
    "status": "POSTED",
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### Status Codes:
- **200 OK** → Statement retrieved successfully
- **401 Unauthorized** → Authentication required
- **404 Not Found** → Account type not found

### Authentication:
Required (Bearer token)

---

## 4. 🔄 API Flow

### Deposit Flow (M-Pesa STK Push)

1. **User Initiates Deposit**: User calls `/api/deposits/initiate/` with amount, target wallet, and phone number
2. **Backend Sends STK Push**: System processes request and sends M-Pesa STK push to user's phone
3. **User Enters PIN**: User receives prompt on phone and enters M-Pesa PIN
4. **Safaricom Sends Callback**: M-Pesa calls `/api/mpesa/callback/` with transaction result
5. **Backend Updates Transaction**: System processes callback, updates deposit status, and credits user's wallet

### Withdrawal Flow (M-Pesa B2C)

1. **User Requests Withdrawal**: User calls `/api/withdrawals/request/` with amount and phone number
2. **Backend Validates Request**: System checks wallet balance and validates withdrawal request
3. **Backend Sends B2C Request**: System initiates M-Pesa B2C transfer to user's phone
4. **Safaricom Processes Request**: M-Pesa processes the withdrawal and sends money to user
5. **Callback Updates Transaction**: M-Pesa calls `/api/withdrawals/callback/` with transaction result
6. **Backend Finalizes Withdrawal**: System processes callback, updates withdrawal status, and debits wallet

### Payment Flow (QR-based)

1. **Student Generates QR**: Student calls `/api/qr/generate/` to create dynamic QR token
2. **Merchant Scans QR**: Merchant scans QR code using POS terminal
3. **Merchant Validates Token**: POS calls `/api/qr/validate/{token}/` to verify token validity
4. **Merchant Creates Payment Intent**: POS calls `/api/payments/intent/create/` to initiate payment
5. **Student Confirms Payment**: System matches QR token with payment intent
6. **Payment Processed**: System transfers funds from student's wallet to merchant's settlement account
7. **Notifications Sent**: Both parties receive transaction notifications

---

## 5. 🗄️ Data Models

### User

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| email | String | User email address (unique) |
| phone | String | Phone number (unique, format: 07XXXXXXXXX) |
| first_name | String | User's first name |
| last_name | String | User's last name |
| is_active | Boolean | Account status |
| is_staff | Boolean | Admin access flag |
| roles | Array | User's assigned roles |

### UserRole

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| user | UUID | Reference to User |
| role | String | Role type (STUDENT, CUSTOMER, BUSINESS, ADMIN) |

### Student

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| user | UUID | Reference to User |
| reg_no | String | Registration number (unique) |
| created_at | DateTime | Profile creation timestamp |

### Business

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| user | UUID | Reference to User |
| name | String | Business name |
| category_code | String | Business category (FOOD, OTHERS) |
| mpesa_till_number | String | M-Pesa till number |
| is_active | Boolean | Business status |
| terminals | Array | Registered POS terminals |

### BusinessTerminal

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| business | UUID | Reference to Business |
| device_id | String | Terminal device ID (unique per business) |
| location | String | Physical location |
| is_online | Boolean | Online status |

### Wallet

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| owner_type | String | Owner type (STUDENT, CUSTOMER, BUSINESS) |
| owner_id | UUID | Owner's user ID |
| type | String | Wallet type (MEAL, POCKET, PERSONAL, SETTLEMENT) |
| balance | Decimal | Current balance |
| created_at | DateTime | Wallet creation timestamp |

### PaymentIntent

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| terminal | UUID | POS terminal reference |
| amount | Decimal | Payment amount |
| status | String | Intent status (PENDING, COMPLETED, EXPIRED) |
| expires_at | DateTime | Expiration timestamp |

### QRToken

| Field | Type | Description |
| ------ | ------ | ----------- |
| token | String | Token value |
| amount | Decimal | Payment amount |
| wallet_type | String | Source wallet type |
| owner | UUID | Token owner |
| expires_at | DateTime | Expiration timestamp |

### Transaction

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| from_wallet | UUID | Source wallet |
| to_wallet | UUID | Destination wallet |
| amount | Decimal | Transaction amount |
| status | String | Transaction status |
| reference | String | Transaction reference |
| created_at | DateTime | Transaction timestamp |

### Deposit

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| user | UUID | Depositing user |
| amount | Decimal | Deposit amount |
| target_wallet | String | Destination wallet type |
| phone_number | String | M-Pesa phone number |
| status | String | Deposit status (PENDING, SUCCESS, FAILED) |
| mpesa_request_id | String | M-Pesa request ID |
| mpesa_receipt | String | M-Pesa receipt number |

### Withdrawal

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| user | UUID | Withdrawing user |
| amount | Decimal | Withdrawal amount |
| phone_number | String | Destination phone |
| status | String | Withdrawal status (PENDING, SUCCESS, FAILED) |
| transaction_id | String | M-Pesa transaction ID |

### Notification

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| user | UUID | Notification recipient |
| title | String | Notification title |
| message | String | Notification message |
| type | String | Notification type |
| read | Boolean | Read status |
| created_at | DateTime | Creation timestamp |

### LedgerAccount

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| owner_id | UUID | Account owner |
| account_type | String | Account type (STUDENT_MEAL, STUDENT_POCKET, etc.) |
| balance | Decimal | Current balance |

### LedgerEntry

| Field | Type | Description |
| ------ | ------ | ----------- |
| id | UUID | Unique identifier |
| debit_account | UUID | Account being debited |
| credit_account | UUID | Account being credited |
| amount | Decimal | Entry amount |
| reference | String | Entry reference |
| description | String | Entry description |
| status | String | Entry status |
| created_at | DateTime | Entry timestamp |

---

## 6. ❗ Error Handling

### Common Error Responses

#### Validation Errors (400 Bad Request)
```json
{
  "email": ["This field is required."],
  "phone": ["Phone number must be in format 07XXXXXXXXX"]
}
```

#### Authentication Errors (401 Unauthorized)
```json
{
  "error": "Invalid Credentials"
}
```

#### Permission Errors (403 Forbidden)
```json
{
  "error": "You do not have permission to perform this action"
}
```

#### Not Found Errors (404 Not Found)
```json
{
  "error": "Resource not found"
}
```

#### Server Errors (500 Internal Server Error)
```json
{
  "error": "Internal server error occurred"
}
```

#### M-Pesa Integration Errors
```json
{
  "error": "M-Pesa service unavailable",
  "details": "Unable to reach M-Pesa API"
}
```

---

## 7. ⚙️ Environment Variables

### Collection Variables

| Variable | Type | Description |
| -------- | ------ | ----------- |
| base_url | String | API base URL (default: http://127.0.0.1:8000) |
| access_token | String | JWT access token for authenticated requests |
| refresh_token | String | JWT refresh token for token renewal |

### Authentication Setup

1. **Set Base URL**: Configure `base_url` to point to your EasyPay instance
2. **Login**: Use `/api/accounts/login/` to obtain tokens
3. **Set Tokens**: Save `access` token to `access_token` variable
4. **Use Auth**: Collection automatically uses Bearer token for protected endpoints

### Development Environment
- **Base URL**: `http://127.0.0.1:8000`
- **Content-Type**: `application/json`
- **Authentication**: Bearer token in Authorization header

---

## 📋 Quick Reference

### Common Status Codes
- **200 OK** → Request successful
- **201 Created** → Resource created successfully
- **400 Bad Request** → Validation error
- **401 Unauthorized** → Authentication required or invalid
- **403 Forbidden** → Permission denied
- **404 Not Found** → Resource not found
- **500 Internal Server Error** → Server error

### Authentication Flow
1. `POST /api/accounts/register/` → Create account
2. `POST /api/accounts/login/` → Get tokens
3. Set `access_token` variable
4. Make authenticated requests
5. `POST /api/accounts/logout/` → Logout

### Wallet Types
- **MEAL**: Student meal allowance wallet
- **POCKET**: Student personal spending wallet
- **PERSONAL**: Guardian/personal wallet
- **SETTLEMENT**: Merchant settlement wallet

### User Roles
- **STUDENT**: Can make payments, generate QR codes
- **CUSTOMER/Guardian**: Can top up student wallets, view transactions
- **BUSINESS/Merchant**: Can receive payments, manage terminals
- **ADMIN**: Full system access
