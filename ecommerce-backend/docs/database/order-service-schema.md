# Order Service Database Schema

## Database: order_service_db (PostgreSQL)

This database handles order processing, tracking, and history.

---

## Tables

### 1. orders
Customer orders.

**Fields:**
- `id` (UUID, Primary Key) - Order ID
- `order_number` (VARCHAR(50), UNIQUE, NOT NULL) - Human-readable order number (e.g., ORD-2024-00001)
- `user_id` (UUID, NOT NULL) - References users.id (from User Service)
- `status` (ENUM, NOT NULL) - Order status
  - Values: 'PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED'
- `subtotal` (DECIMAL(10,2), NOT NULL) - Items total
- `tax_amount` (DECIMAL(10,2), DEFAULT 0) - Tax
- `shipping_amount` (DECIMAL(10,2), DEFAULT 0) - Shipping cost
- `discount_amount` (DECIMAL(10,2), DEFAULT 0) - Discounts applied
- `total_amount` (DECIMAL(10,2), NOT NULL) - Final total
- `currency` (VARCHAR(3), DEFAULT 'USD')
- `shipping_address_id` (UUID, NOT NULL) - References user_addresses.id
- `billing_address_id` (UUID, NOT NULL) - References user_addresses.id
- `notes` (TEXT, NULLABLE) - Customer notes
- `tracking_number` (VARCHAR(100), NULLABLE) - Shipping tracking
- `shipped_at` (TIMESTAMP, NULLABLE)
- `delivered_at` (TIMESTAMP, NULLABLE)
- `cancelled_at` (TIMESTAMP, NULLABLE)
- `cancellation_reason` (TEXT, NULLABLE)
- `created_at` (TIMESTAMP, DEFAULT NOW())
- `updated_at` (TIMESTAMP, AUTO UPDATE)

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `order_number`
- INDEX on `user_id`
- INDEX on `status`
- INDEX on `created_at`

**Django Model Considerations:**
- Use `TextChoices` for status enum
- Auto-generate order_number (ORD-YYYY-NNNNN)
- Use `DecimalField` for all money fields

---

### 2. order_items
Items within an order.

**Fields:**
- `id` (UUID, Primary Key)
- `order_id` (UUID, Foreign Key -> orders.id, NOT NULL)
- `product_id` (UUID, NOT NULL) - References products.id (from Product Service)
- `product_name` (VARCHAR(255), NOT NULL) - Snapshot of product name
- `product_sku` (VARCHAR(100), NOT NULL) - Snapshot of SKU
- `quantity` (INTEGER, NOT NULL)
- `unit_price` (DECIMAL(10,2), NOT NULL) - Price at time of order
- `total_price` (DECIMAL(10,2), NOT NULL) - quantity * unit_price
- `created_at` (TIMESTAMP, DEFAULT NOW())

**Constraints:**
- FOREIGN KEY `order_id` REFERENCES `orders(id)` ON DELETE CASCADE
- CHECK constraint: `quantity > 0`
- CHECK constraint: `unit_price >= 0`

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `order_id`
- INDEX on `product_id`

**Django Model Considerations:**
- Store product snapshot (name, sku, price) to preserve order history
- ForeignKey with `related_name='items'`
- Calculate total_price automatically

---

### 3. order_status_history
Tracks order status changes.

**Fields:**
- `id` (UUID, Primary Key)
- `order_id` (UUID, Foreign Key -> orders.id, NOT NULL)
- `from_status` (VARCHAR(50), NULLABLE) - Previous status
- `to_status` (VARCHAR(50), NOT NULL) - New status
- `notes` (TEXT, NULLABLE)
- `changed_by` (UUID, NULLABLE) - User/Admin who changed it
- `created_at` (TIMESTAMP, DEFAULT NOW())

**Constraints:**
- FOREIGN KEY `order_id` REFERENCES `orders(id)` ON DELETE CASCADE

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `order_id`

**Django Model Considerations:**
- Use signals to auto-create history on status change
- ForeignKey with `related_name='status_history'`

---

## Relationships

### orders → order_items (One-to-Many)
- One order contains multiple items
- One item belongs to one order
- **Cardinality: 1:N**

### orders → order_status_history (One-to-Many)
- One order has multiple status changes
- One status change belongs to one order
- **Cardinality: 1:N**

---

## Foreign Keys Summary

- `order_items(order_id)` REFERENCES `orders(id)` ON DELETE CASCADE
- `order_status_history(order_id)` REFERENCES `orders(id)` ON DELETE CASCADE

---

## Cross-Service References (Logical)

### From Other Services:
- `orders.user_id` → User Service: `users.id`
- `orders.shipping_address_id` → User Service: `user_addresses.id`
- `orders.billing_address_id` → User Service: `user_addresses.id`
- `order_items.product_id` → Product Service: `products.id`

### To Other Services:
- `orders.id` → Payment Service: `transactions.order_id`

---

## Order Status Flow

```
PENDING (Order created, awaiting payment)
    ↓
CONFIRMED (Payment confirmed)
    ↓
PROCESSING (Being prepared)
    ↓
SHIPPED (Out for delivery)
    ↓
DELIVERED (Completed)

Alternative flows:
PENDING/CONFIRMED → CANCELLED (Cancelled by user/admin)
DELIVERED → REFUNDED (Refund processed)
```

---

## Kafka Events

### Producer Events:
- `order.created` - When order is placed
- `order.confirmed` - When payment confirmed
- `order.shipped` - When order shipped
- `order.delivered` - When order delivered
- `order.cancelled` - When order cancelled

### Consumer Events:
- `payment.confirmed` - Update order status to CONFIRMED
- `payment.failed` - Cancel order

---

## APIs That Will Use This Schema

- POST `/api/orders` - Create new order
- GET `/api/orders` - Get user's order history
- GET `/api/orders/:id` - Get order details
- PUT `/api/orders/:id/status` - Update order status (Admin)
- GET `/api/orders/:id/tracking` - Track order delivery
- POST `/api/orders/:id/cancel` - Cancel order

---

## Business Logic

### Order Creation Process:
1. User initiates checkout from cart
2. Validate cart items and inventory
3. Calculate totals (subtotal, tax, shipping)
4. Create order with status=PENDING
5. Reserve inventory (increment reserved_quantity)
6. Trigger payment process
7. Kafka event: `order.created`

### Order Confirmation (on payment success):
1. Update order status to CONFIRMED
2. Decrement actual inventory
3. Clear reserved_quantity
4. Kafka event: `order.confirmed`
5. Trigger notification: order confirmation email

### Order Cancellation:
1. Check if order can be cancelled (not SHIPPED/DELIVERED)
2. Update status to CANCELLED
3. Release inventory (decrement reserved_quantity)
4. Trigger refund if payment was made
5. Kafka event: `order.cancelled`

---

## Sample Data

### orders
```sql
INSERT INTO orders (id, order_number, user_id, status, subtotal, tax_amount, shipping_amount, total_amount)
VALUES 
  ('ord-1', 'ORD-2024-00001', 'user-1', 'DELIVERED', 2499.99, 249.99, 10.00, 2759.98),
  ('ord-2', 'ORD-2024-00002', 'user-2', 'PROCESSING', 999.99, 99.99, 5.00, 1104.98);
```

### order_items
```sql
INSERT INTO order_items (id, order_id, product_id, product_name, product_sku, quantity, unit_price, total_price)
VALUES 
  ('item-1', 'ord-1', 'prod-1', 'MacBook Pro 16"', 'MBP-16-001', 1, 2499.99, 2499.99),
  ('item-2', 'ord-2', 'prod-2', 'iPhone 15 Pro', 'IPH-15P-001', 1, 999.99, 999.99);
```
