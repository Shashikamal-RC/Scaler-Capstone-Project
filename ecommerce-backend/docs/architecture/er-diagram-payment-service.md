# Payment Service ER Diagram

## Entity Relationship Diagram - Payment Service

This document provides the structure for creating the ER diagram in draw.io.

---

## Entities and Attributes

### 1. payment_methods (Lookup Entity)
**Attributes:**
- 🔑 id (PK) - SERIAL
- 📝 name (UNIQUE) - VARCHAR(50)
  - CREDIT_CARD
  - DEBIT_CARD
  - UPI
  - NET_BANKING
  - WALLET
  - COD (Cash on Delivery)
- 📝 description - TEXT
- ✓ is_active - BOOLEAN
- 🔢 display_order - INTEGER
- 📅 created_at - TIMESTAMP
- 📅 updated_at - TIMESTAMP

### 2. transactions (Main Entity)
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 order_id - UUID (External reference to Order Service)
- 🔗 user_id - UUID (External reference to User Service)
- 🔗 payment_method_id (FK) - INTEGER → payment_methods.id
- 💰 amount - DECIMAL(10,2)
- 💱 currency - VARCHAR(3) (e.g., 'INR', 'USD')
- 📊 status - ENUM
  - INITIATED
  - PROCESSING
  - SUCCESS
  - FAILED
  - CANCELLED
  - REFUNDED
- 🔐 transaction_id (UNIQUE) - VARCHAR(100)
- 🏦 gateway_transaction_id - VARCHAR(100)
- 🏦 gateway_name - VARCHAR(50) (e.g., 'Razorpay', 'Stripe')
- 📝 gateway_response - JSONB
- 💳 payment_details - JSONB (masked card details, UPI ID, etc.)
- 📝 failure_reason - TEXT
- 📅 initiated_at - TIMESTAMP
- 📅 completed_at - TIMESTAMP
- 📅 created_at - TIMESTAMP
- 📅 updated_at - TIMESTAMP

### 3. user_saved_payment_methods
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 user_id - UUID (External reference to User Service)
- 🔗 payment_method_id (FK) - INTEGER → payment_methods.id
- 🔐 token - VARCHAR(255) (Encrypted gateway token)
- 💳 last_four_digits - VARCHAR(4)
- 📛 card_brand - VARCHAR(50) (e.g., 'Visa', 'Mastercard')
- 📛 nickname - VARCHAR(100) (e.g., 'My HDFC Card')
- 📅 expiry_month - INTEGER
- 📅 expiry_year - INTEGER
- ✓ is_default - BOOLEAN
- ✓ is_active - BOOLEAN
- 📅 created_at - TIMESTAMP
- 📅 updated_at - TIMESTAMP

---

## Relationships

### 1. payment_methods → transactions (One-to-Many)
```
payment_methods ──────|──────< transactions
        1                    N
```
- **Cardinality:** 1:N
- **Relationship:** One payment method can be used in multiple transactions
- **Foreign Key:** transactions.payment_method_id → payment_methods.id
- **ON DELETE:** RESTRICT (Cannot delete if transactions exist)

### 2. payment_methods → user_saved_payment_methods (One-to-Many)
```
payment_methods ──────|──────< user_saved_payment_methods
        1                            N
```
- **Cardinality:** 1:N
- **Relationship:** One payment method type can have multiple saved instances
- **Foreign Key:** user_saved_payment_methods.payment_method_id → payment_methods.id
- **ON DELETE:** RESTRICT

---

## Draw.io Instructions

### Layout Suggestion:
```
┌────────────────────────────────────────────────────────────────┐
│                                                                  │
│                   ┌─────────────────┐                          │
│                   │payment_methods  │                          │
│                   │  (Lookup)       │                          │
│                   │                 │                          │
│                   │ - id (PK)       │                          │
│                   │ - name          │                          │
│                   │   • CREDIT_CARD │                          │
│                   │   • DEBIT_CARD  │                          │
│                   │   • UPI         │                          │
│                   │   • NET_BANKING │                          │
│                   │   • WALLET      │                          │
│                   │   • COD         │                          │
│                   │ - description   │                          │
│                   │ - is_active     │                          │
│                   │ - display_order │                          │
│                   └────────┬────────┘                          │
│                            │ 1                                  │
│                ┌───────────┴──────────────┐                    │
│                │                          │                    │
│              N │                        N │                    │
│                │                          │                    │
│   ┌────────────┴────────────┐  ┌─────────┴──────────────────┐ │
│   │    transactions         │  │ user_saved_payment_methods │ │
│   │     (Main Entity)       │  │                            │ │
│   │                         │  │                            │ │
│   │ - id (PK)               │  │ - id (PK)                  │ │
│   │ - order_id              │  │ - user_id                  │ │
│   │ - user_id               │  │ - payment_method_id (FK)   │ │
│   │ - payment_method_id(FK) │  │ - token (Encrypted)        │ │
│   │ - amount                │  │ - last_four_digits         │ │
│   │ - currency              │  │ - card_brand               │ │
│   │ - status                │  │ - nickname                 │ │
│   │ - transaction_id        │  │ - expiry_month             │ │
│   │ - gateway_transaction_id│  │ - expiry_year              │ │
│   │ - gateway_name          │  │ - is_default               │ │
│   │ - gateway_response      │  │ - is_active                │ │
│   │ - payment_details       │  │                            │ │
│   │ - failure_reason        │  │                            │ │
│   │ - initiated_at          │  │                            │ │
│   │ - completed_at          │  │                            │ │
│   └─────────────────────────┘  └────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Entity Styling:

1. **payment_methods (Lookup)**
   - Color: Light yellow (#FEF9E7)
   - Border: 2px solid gold
   - Position: Top-center

2. **transactions (Main Entity)**
   - Color: Light blue (#D6EAF8)
   - Border: 2px solid blue
   - Position: Bottom-left

3. **user_saved_payment_methods**
   - Color: Light green (#D5F4E6)
   - Border: 2px solid green
   - Position: Bottom-right

---

## Payment Transaction Flow Diagram

Create a separate flow diagram showing payment lifecycle:

```
┌───────────────────────────────────────────────────────────────┐
│                  Payment Transaction Flow                      │
│                                                                 │
│         [User initiates payment]                               │
│                    │                                           │
│                    ▼                                           │
│              [INITIATED]                                       │
│                    │                                           │
│                    ▼                                           │
│          Send to Payment Gateway                               │
│                    │                                           │
│                    ▼                                           │
│              [PROCESSING]                                      │
│                    │                                           │
│           ┌────────┴────────┐                                 │
│           │                 │                                 │
│           ▼                 ▼                                 │
│      [SUCCESS]         [FAILED]                               │
│           │                 │                                 │
│           │                 └─────► [End]                     │
│           │                                                    │
│           ├─────► Update Order                                │
│           │       Status to PAID                              │
│           │                                                    │
│           └─────► [Can be REFUNDED]                           │
│                          │                                     │
│                          ▼                                     │
│                    [REFUNDED]                                  │
│                          │                                     │
│                          └─────► Update Order                  │
│                                  Status                        │
│                                                                 │
│   Note: [CANCELLED] can occur from INITIATED or PROCESSING     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cross-Service Relationships (Logical References)

```
┌──────────────┐
│Order Service │
└──────┬───────┘
       ┊ (Logical FK)
       ┊
       ▼
┌──────────────────┐
│  transactions    │
│  - order_id      │
│  - user_id       │◄┈┈┈┈ User Service (users.id)
└──────────────────┘

┌──────────────┐
│User Service  │
└──────┬───────┘
       ┊
       ▼
┌────────────────────────────┐
│user_saved_payment_methods  │
│  - user_id                 │
└────────────────────────────┘
```

---

## Security Considerations

### 1. PCI-DSS Compliance
```
❌ DO NOT store:
   - Full card number
   - CVV/CVC
   - PIN

✅ DO store:
   - Encrypted gateway token
   - Last 4 digits only
   - Card brand (Visa, Mastercard)
   - Expiry month/year
```

### 2. Encryption
- `user_saved_payment_methods.token`: **Encrypted** at rest
- `transactions.payment_details`: Store only masked data in JSONB
- `transactions.gateway_response`: Gateway response (can contain sensitive data, encrypt if needed)

### 3. Audit Trail
All transactions are logged with:
- initiated_at: When payment started
- completed_at: When payment finished
- gateway_response: Full response from gateway
- status: Current state

---

## Payment Gateway Integration

### Supported Gateways:
1. **Razorpay** (India)
2. **Stripe** (International)
3. **PayPal**
4. **Paytm**

### Gateway Response Example (JSONB):
```json
{
  "gateway": "Razorpay",
  "transaction_id": "pay_KhOQPwQwFhRxQX",
  "order_id": "order_KhOQOWbBAY6Tl9",
  "status": "captured",
  "method": "card",
  "card": {
    "last4": "1234",
    "network": "Visa",
    "type": "credit"
  },
  "bank": "HDFC Bank",
  "error_code": null,
  "error_description": null
}
```

---

## Business Rules

### 1. Transaction States:
```
INITIATED → PROCESSING → SUCCESS
                ↓          ↓
             FAILED    REFUNDED
                ↓
           CANCELLED
```

### 2. Refund Logic:
- Only SUCCESS transactions can be REFUNDED
- Partial refunds allowed
- Create new transaction with negative amount

### 3. Saved Payment Methods:
- One `is_default` per user
- Store only tokenized card details
- Never store actual card numbers

### 4. Currency Handling:
- Store in original currency
- Display converted values in frontend
- Default currency: INR

---

## Indexes for Performance

```sql
-- Transactions table
CREATE INDEX idx_transactions_order_id ON transactions(order_id);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_transaction_id ON transactions(transaction_id);
CREATE INDEX idx_transactions_initiated_at ON transactions(initiated_at DESC);

-- User saved payment methods
CREATE INDEX idx_user_saved_pm_user_id ON user_saved_payment_methods(user_id);
CREATE INDEX idx_user_saved_pm_is_default ON user_saved_payment_methods(user_id, is_default);
```

---

## Sample Queries

### Get User's Transaction History:
```sql
SELECT * FROM transactions
WHERE user_id = <user_id>
ORDER BY initiated_at DESC;
```

### Get Order Payment Status:
```sql
SELECT status, amount, gateway_name, completed_at
FROM transactions
WHERE order_id = <order_id>
AND status = 'SUCCESS';
```

### Get User's Saved Cards:
```sql
SELECT pm.name, uspm.last_four_digits, uspm.card_brand, uspm.nickname
FROM user_saved_payment_methods uspm
JOIN payment_methods pm ON uspm.payment_method_id = pm.id
WHERE uspm.user_id = <user_id>
AND uspm.is_active = TRUE;
```

---

## Data Integrity Notes

### Constraints:
- transaction_id: UNIQUE across all transactions
- amount: CHECK (amount > 0) for normal transactions
- currency: DEFAULT 'INR'
- last_four_digits: CHECK (LENGTH = 4)

### Cascade Rules:
- Delete payment_method → RESTRICT (if used in transactions)
- Delete payment_method → RESTRICT (if saved by users)

---

## Export Instructions

1. Create main ER diagram with 3 entities
2. Create payment flow state diagram
3. Create cross-service reference diagram
4. Export as:
   - PNG (300 DPI for report)
   - SVG (for documentation)
   - PDF (for presentations)

Recommended size: 1920x1080 or A4 landscape

---

## Figure Captions for Report

**Figure X.5: Payment Service Entity-Relationship Diagram**

*The Payment Service schema comprises three entities: payment_methods (lookup table for payment types), transactions (main entity storing payment details and gateway responses), and user_saved_payment_methods (tokenized payment information for quick checkout). The schema enforces PCI-DSS compliance by never storing sensitive card data, using encrypted tokens instead. Relationships are one-to-many from payment_methods to both transactions and saved methods.*

**Figure X.6: Payment Transaction State Diagram**

*This state diagram illustrates the payment transaction lifecycle with five states: INITIATED, PROCESSING, SUCCESS, FAILED, and REFUNDED. Transactions begin in INITIATED state, progress to PROCESSING when sent to the gateway, and conclude in either SUCCESS or FAILED. Successful transactions can later be REFUNDED. CANCELLED state is accessible from INITIATED or PROCESSING states if the user aborts the payment.*
