# Payment Service Database Schema

## Database: payment_service_db (PostgreSQL)

This database handles payment processing, transactions, and payment methods.

---

## Tables

### 1. payment_methods
Available payment methods.

**Fields:**
- `id` (SERIAL, Primary Key)
- `name` (VARCHAR(50), UNIQUE, NOT NULL) - Method name
- `code` (VARCHAR(20), UNIQUE, NOT NULL) - Method code
  - Values: 'CREDIT_CARD', 'DEBIT_CARD', 'UPI', 'NET_BANKING', 'WALLET', 'COD'
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `display_order` (INTEGER, DEFAULT 0)
- `created_at` (TIMESTAMP, DEFAULT NOW())

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `code`

**Django Model Considerations:**
- Use `TextChoices` for code enum
- Seed default payment methods in migration

---

### 2. transactions
Payment transactions.

**Fields:**
- `id` (UUID, Primary Key) - Transaction ID
- `transaction_number` (VARCHAR(50), UNIQUE, NOT NULL) - Readable transaction number (e.g., TXN-2024-00001)
- `order_id` (UUID, NOT NULL) - References orders.id (from Order Service)
- `user_id` (UUID, NOT NULL) - References users.id (from User Service)
- `payment_method_id` (INTEGER, Foreign Key -> payment_methods.id, NOT NULL)
- `amount` (DECIMAL(10,2), NOT NULL)
- `currency` (VARCHAR(3), DEFAULT 'USD')
- `status` (ENUM, NOT NULL)
  - Values: 'PENDING', 'PROCESSING', 'SUCCESS', 'FAILED', 'REFUNDED', 'CANCELLED'
- `gateway_transaction_id` (VARCHAR(255), NULLABLE) - External gateway ID (Stripe, Razorpay, etc.)
- `gateway_response` (JSONB, NULLABLE) - Gateway response data
- `failure_reason` (TEXT, NULLABLE)
- `processed_at` (TIMESTAMP, NULLABLE)
- `refunded_at` (TIMESTAMP, NULLABLE)
- `refund_amount` (DECIMAL(10,2), NULLABLE)
- `created_at` (TIMESTAMP, DEFAULT NOW())
- `updated_at` (TIMESTAMP, AUTO UPDATE)

**Constraints:**
- FOREIGN KEY `payment_method_id` REFERENCES `payment_methods(id)` ON DELETE RESTRICT
- CHECK constraint: `amount > 0`

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `transaction_number`
- INDEX on `order_id`
- INDEX on `user_id`
- INDEX on `status`
- INDEX on `created_at`

**Django Model Considerations:**
- Use `TextChoices` for status enum
- Use `JSONField` for gateway_response
- Auto-generate transaction_number

---

### 3. user_saved_payment_methods
User's saved payment methods for quick checkout.

**Fields:**
- `id` (UUID, Primary Key)
- `user_id` (UUID, NOT NULL) - References users.id
- `payment_method_id` (INTEGER, Foreign Key -> payment_methods.id, NOT NULL)
- `card_last_four` (VARCHAR(4), NULLABLE) - Last 4 digits of card
- `card_brand` (VARCHAR(20), NULLABLE) - VISA, MASTERCARD, AMEX, etc.
- `expiry_month` (INTEGER, NULLABLE)
- `expiry_year` (INTEGER, NULLABLE)
- `is_default` (BOOLEAN, DEFAULT FALSE)
- `gateway_customer_id` (VARCHAR(255), NULLABLE) - Gateway customer ID
- `gateway_token` (TEXT, NULLABLE) - Encrypted token from payment gateway
- `created_at` (TIMESTAMP, DEFAULT NOW())
- `updated_at` (TIMESTAMP, AUTO UPDATE)

**Constraints:**
- FOREIGN KEY `payment_method_id` REFERENCES `payment_methods(id)` ON DELETE CASCADE
- CHECK constraint: `expiry_month BETWEEN 1 AND 12`

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `user_id`
- INDEX on `payment_method_id`

**Django Model Considerations:**
- Encrypt gateway_token using `cryptography`
- Validate expiry_month and expiry_year
- Only one `is_default=True` per user

---

## Relationships

### payment_methods → transactions (One-to-Many)
- One payment method used in many transactions
- One transaction uses one payment method
- **Cardinality: 1:N**

### payment_methods → user_saved_payment_methods (One-to-Many)
- One payment method type saved multiple times by users
- One saved method is of one payment method type
- **Cardinality: 1:N**

---

## Foreign Keys Summary

- `transactions(payment_method_id)` REFERENCES `payment_methods(id)` ON DELETE RESTRICT
- `user_saved_payment_methods(payment_method_id)` REFERENCES `payment_methods(id)` ON DELETE CASCADE

---

## Cross-Service References (Logical)

### From Other Services:
- `transactions.order_id` → Order Service: `orders.id`
- `transactions.user_id` → User Service: `users.id`
- `user_saved_payment_methods.user_id` → User Service: `users.id`

---

## Payment Status Flow

```
PENDING (Payment initiated)
    ↓
PROCESSING (Being processed by gateway)
    ↓
SUCCESS (Payment successful)
    OR
FAILED (Payment failed)

From SUCCESS:
    ↓
REFUNDED (Refund processed)

From PENDING/PROCESSING:
    ↓
CANCELLED (Payment cancelled)
```

---

## Kafka Events

### Producer Events:
- `payment.initiated` - When payment starts
- `payment.confirmed` - When payment succeeds
- `payment.failed` - When payment fails
- `payment.refunded` - When payment refunded

### Consumer Events:
- `order.created` - Initiate payment for order

---

## Payment Gateway Integration

### Supported Gateways (Mock for now):
- Stripe
- Razorpay
- PayPal

### Payment Flow:
1. User selects payment method at checkout
2. Create transaction with status=PENDING
3. Call payment gateway API
4. Update status based on gateway response
5. Store gateway_transaction_id and gateway_response
6. Kafka event based on result
7. Update order status via Kafka

### Refund Flow:
1. Admin initiates refund
2. Call gateway refund API
3. Update transaction status to REFUNDED
4. Store refund_amount and refunded_at
5. Kafka event: `payment.refunded`
6. Update order status to REFUNDED

---

## Security Considerations

1. **Never store full card numbers** - Only last 4 digits
2. **Encrypt gateway tokens** - Use Django's encryption
3. **PCI DSS compliance** - Use tokenization from payment gateway
4. **HTTPS only** - All payment APIs must use HTTPS
5. **Rate limiting** - Prevent brute force attacks
6. **Audit logging** - Log all payment attempts

---

## APIs That Will Use This Schema

- POST `/api/payments` - Process payment
- GET `/api/payments/:id` - Get payment details
- POST `/api/payments/:id/refund` - Process refund (Admin)
- GET `/api/payments/transaction/:id` - Get transaction details
- POST `/api/payments/methods/save` - Save payment method
- GET `/api/payments/methods` - Get saved payment methods
- DELETE `/api/payments/methods/:id` - Remove saved method

---

## Sample Data

### payment_methods
```sql
INSERT INTO payment_methods (name, code, is_active, display_order)
VALUES 
  ('Credit Card', 'CREDIT_CARD', TRUE, 1),
  ('Debit Card', 'DEBIT_CARD', TRUE, 2),
  ('UPI', 'UPI', TRUE, 3),
  ('Net Banking', 'NET_BANKING', TRUE, 4),
  ('Wallet', 'WALLET', TRUE, 5),
  ('Cash on Delivery', 'COD', TRUE, 6);
```

### transactions
```sql
INSERT INTO transactions (id, transaction_number, order_id, user_id, payment_method_id, amount, status, gateway_transaction_id)
VALUES 
  ('txn-1', 'TXN-2024-00001', 'ord-1', 'user-1', 1, 2759.98, 'SUCCESS', 'stripe_ch_abc123'),
  ('txn-2', 'TXN-2024-00002', 'ord-2', 'user-2', 3, 1104.98, 'PROCESSING', 'razorpay_order_xyz789');
```
