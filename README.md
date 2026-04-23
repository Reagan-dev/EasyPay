# EasyPay

> A closed-loop digital payment platform powering real-time, ledger-driven transactions within controlled ecosystems.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.x-092E20?style=flat-square&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![M-Pesa](https://img.shields.io/badge/M--Pesa-Daraja_API-00A651?style=flat-square)](https://developer.safaricom.co.ke/)

---

## Overview

EasyPay replaces slow, cash-heavy and manual mobile money workflows with a **two-layer financial architecture**: an internal ledger for sub-second day-to-day transactions, and M-Pesa (Daraja API) as the external on/off-ramp for deposits and withdrawals.

The platform connects four user roles — **Students, Guardians, Merchants, and Administrators** — through a unified API, supporting QR-based point-of-sale payments, programmable wallet controls, and a complete financial audit trail.

### The Problem It Solves

In institutional environments (schools, campuses, controlled marketplaces), traditional mobile money creates friction: every transaction requires manual STK push flows, there's no spending visibility, and merchants have no reliable settlement mechanism. EasyPay collapses that into a scan-and-go experience backed by a real-time internal ledger.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    EasyPay Platform                     │
│                                                         │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐  │
│   │ Students │  │Guardians │  │Merchants │  │Admin │  │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └──┬───┘  │
│        │              │              │            │      │
│        └──────────────┴──────────────┴────────────┘     │
│                          │                               │
│              ┌───────────▼────────────┐                  │
│              │   Django REST API      │                  │
│              │   (JWT Auth + RBAC)    │                  │
│              └───────────┬────────────┘                  │
│                          │                               │
│          ┌───────────────┼────────────────┐              │
│          │               │                │              │
│   ┌──────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐       │
│   │   Internal  │  │  QR Token  │  │ Wallet &   │       │
│   │   Ledger    │  │   Engine   │  │  Balances  │       │
│   └─────────────┘  └────────────┘  └─────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          │
              ┌───────────▼────────────┐
              │  M-Pesa Daraja API     │
              │  STK Push │ B2C        │
              └────────────────────────┘
```

**Internal layer** handles all day-to-day transactions atomically (sub-second, no external API calls).

**External layer** (M-Pesa) is only invoked on deposit (STK Push) and withdrawal (B2C). This keeps costs low and speeds high.

---

## Key Features

- **Closed-Loop Payments** — funds enter via M-Pesa and circulate internally through the ledger; no external API call per transaction
- **QR Token Payments** — time-sensitive QR codes enable scan-and-go merchant payments (intent expires in 60 seconds)
- **Smart Wallets** — multiple wallet types per user (`MEAL`, `POCKET`, `PERSONAL`, `SETTLEMENT`) with programmable controls
- **Multi-Role RBAC** — four distinct roles (Student, Guardian, Merchant, Admin) with scoped permissions and tailored endpoints
- **Guardian Controls** — parents can link to student accounts, top up wallets, and monitor transaction history
- **POS Terminal Management** — merchants register and manage physical terminals; payments are initiated per-device
- **Real-Time Ledger** — all transactions are processed atomically with full audit trails and account statements
- **JWT Authentication** — short-lived access tokens + long-lived refresh tokens with token blacklisting on logout

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django + Django REST Framework |
| Authentication | JWT (SimpleJWT) with token blacklisting |
| Database | PostgreSQL (UUID primary keys throughout) |
| Payment Gateway | M-Pesa Daraja API (STK Push + B2C) |
| API Style | RESTful with role-based access control |

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- An active [Safaricom Daraja API](https://developer.safaricom.co.ke/) account (for M-Pesa features)

### Installation

```bash
# Clone the repository
git clone https://github.com/Reagan-dev/EasyPay.git
cd EasyPay

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root. See `.env.example` for all required variables:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=easypay_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# M-Pesa Daraja API
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/payments/mpesa/callback/
```

### Run the Application

```bash
# Apply migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

---

## API Overview

All endpoints are prefixed with `/api/`. Authentication uses Bearer tokens in the `Authorization` header.

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/accounts/register/` | Register a new user with role | No |
| `POST` | `/api/accounts/login/` | Login, returns JWT tokens | No |
| `POST` | `/api/accounts/logout/` | Blacklist refresh token | Required |
| `POST` | `/api/accounts/token/refresh/` | Refresh access token | No |
| `GET` | `/api/accounts/me/` | Get authenticated user profile | Required |

### Wallets

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/wallets/` | List all wallets with balances | Required |
| `GET` | `/api/wallets/{wallet_type}/` | Get wallet by type (MEAL, POCKET, etc.) | Required |

### Payments

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/payments/intent/create/` | Create a QR payment intent (expires 60s) | Required |
| `GET` | `/api/payments/intent/{uuid}/` | Poll payment intent status | Required |

### Merchants

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/merchants/profile/` | Get business profile + terminals | Required |
| `PATCH` | `/api/merchants/profile/` | Update business profile | Required |
| `GET` | `/api/merchants/terminals/` | List registered POS terminals | Required |
| `POST` | `/api/merchants/terminals/` | Register a new POS terminal | Required |

### Guardians

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/guardians/profile/` | Get guardian profile | Required |
| `GET` | `/api/guardians/students/` | List linked students | Required |
| `POST` | `/api/guardians/students/` | Link a student by reg number | Required |

### Example: Login Request

```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

```json
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "roles": [{ "role": "STUDENT" }]
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1Qi...",
    "refresh": "eyJ0eXAiOiJKV1Qi..."
  }
}
```

### Example: Create Payment Intent (Merchant POS)

```bash
curl -X POST http://localhost:8000/api/payments/intent/create/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "terminal": "uuid-of-registered-terminal",
    "amount": 150.00
  }'
```

---

## User Roles

| Role | Description |
|---|---|
| `STUDENT` | End user — holds wallets, makes payments via QR |
| `GUARDIAN` | Links to students, tops up wallets, monitors transactions |
| `MERCHANT` | Operates POS terminals, receives payments, manages settlement |
| `ADMIN` | Full system access — manages users, disputes, and platform settings |

---

## Wallet Types

| Wallet | Purpose |
|---|---|
| `MEAL` | Restricted to food/canteen merchants |
| `POCKET` | General-purpose spending wallet |
| `PERSONAL` | Personal savings or secondary wallet |
| `SETTLEMENT` | Merchant settlement wallet |

---

## Project Structure

```
EasyPay/
├── accounts/          # User registration, login, JWT auth
├── students/          # Student profiles and management
├── guardians/         # Guardian profiles and student linking
├── merchants/         # Business profiles and POS terminals
├── wallets/           # Wallet models, balances, and ledger
├── payments/          # Payment intents, M-Pesa callbacks, QR logic
├── core/              # Shared utilities, base models, permissions
├── config/            # Django settings and URL routing
├── .env.example       # Environment variable template
├── requirements.txt   # Python dependencies
└── manage.py
```

---

## Design Decisions

**Why closed-loop?** Every external payment API call (M-Pesa STK Push) adds 3-10 seconds of latency and incurs a transaction cost. By maintaining an internal ledger, EasyPay reduces day-to-day transaction time to sub-second while cutting operational costs dramatically.

**Why UUID primary keys?** UUIDs prevent enumeration attacks on financial records — a sequential integer ID leaks how many transactions exist in the system.

**Why QR intents expire in 60 seconds?** Time-limited payment tokens prevent replay attacks at POS terminals. A merchant generates the intent; the student's QR scan must happen within the window.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Built with Django REST Framework · PostgreSQL · M-Pesa Daraja API*
