# Order Service ER Diagram

## Entity Relationship Diagram - Order Service

This document provides the structure for creating the ER diagram in draw.io.

---

## Entities and Attributes

### 1. orders (Main Entity)
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 user_id - UUID (External reference to User Service)
- 📝 order_number (UNIQUE) - VARCHAR(50)
- 💰 subtotal - DECIMAL(10,2)
- 💰 tax_amount - DECIMAL(10,2)
- 💰 shipping_amount - DECIMAL(10,2)
- 💰 discount_amount - DECIMAL(10,2)
- 💰 total_amount - DECIMAL(10,2)
- 📊 status - ENUM
  - PENDING
  - CONFIRMED
  - PROCESSING
  - SHIPPED
  - DELIVERED
  - CANCELLED
  - REFUNDED
- 💳 payment_method - VARCHAR(50)
- 💳 payment_status - ENUM('PENDING', 'PAID', 'FAILED', 'REFUNDED')
- 🔗 shipping_address_id - UUID (External reference to User Service)
- 🔗 billing_address_id - UUID (External reference to User Service)
- 📝 tracking_number - VARCHAR(100)
- 🚚 carrier - VARCHAR(100)
- 📝 notes - TEXT
- 📅 order_date - TIMESTAMP
- 📅 shipped_date - TIMESTAMP
- 📅 delivered_date - TIMESTAMP
- 📅 created_at - TIMESTAMP
- 📅 updated_at - TIMESTAMP

### 2. order_items (Child Entity)
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 order_id (FK) - UUID → orders.id
- 🔗 product_id - UUID (External reference to Product Service)
- 📝 product_name - VARCHAR(255) (Snapshot)
- 📦 product_sku - VARCHAR(100) (Snapshot)
- 💰 price - DECIMAL(10,2) (Snapshot)
- 🔢 quantity - INTEGER
- 💰 subtotal - DECIMAL(10,2)
- 📅 created_at - TIMESTAMP

### 3. order_status_history (Audit Trail)
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 order_id (FK) - UUID → orders.id
- 📊 old_status - VARCHAR(50)
- 📊 new_status - VARCHAR(50)
- 📝 comment - TEXT
- 👤 changed_by - UUID (External reference to User Service)
- 📅 changed_at - TIMESTAMP

---

## Relationships

### 1. orders → order_items (One-to-Many)
```
orders ──────|──────< order_items
   1                N
```
- **Cardinality:** 1:N
- **Relationship:** One order contains multiple items
- **Foreign Key:** order_items.order_id → orders.id
- **ON DELETE:** CASCADE
- **Business Rule:** Minimum 1 item per order

### 2. orders → order_status_history (One-to-Many)
```
orders ──────|──────< order_status_history
   1                N
```
- **Cardinality:** 1:N
- **Relationship:** One order has multiple status change records
- **Foreign Key:** order_status_history.order_id → orders.id
- **ON DELETE:** CASCADE
- **Purpose:** Complete audit trail of order lifecycle

---

## Draw.io Instructions

### Layout Suggestion:
```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│                    ┌────────────────┐                        │
│                    │     orders     │                        │
│                    │   (Central)    │                        │
│                    │                │                        │
│                    │ - id (PK)      │                        │
│                    │ - user_id      │                        │
│                    │ - order_number │                        │
│                    │ - subtotal     │                        │
│                    │ - tax_amount   │                        │
│                    │ - shipping_amt │                        │
│                    │ - discount_amt │                        │
│                    │ - total_amount │                        │
│                    │ - status       │                        │
│                    │ - payment_     │                        │
│                    │   method       │                        │
│                    │ - payment_     │                        │
│                    │   status       │                        │
│                    │ - shipping_    │                        │
│                    │   address_id   │                        │
│                    │ - billing_     │                        │
│                    │   address_id   │                        │
│                    │ - tracking_    │                        │
│                    │   number       │                        │
│                    │ - carrier      │                        │
│                    │ - order_date   │                        │
│                    │ - shipped_date │                        │
│                    │ - delivered_   │                        │
│                    │   date         │                        │
│                    └────────┬───────┘                        │
│                             │ 1                              │
│                ┌────────────┴──────────┐                     │
│                │                       │                     │
│              N │                     N │                     │
│                │                       │                     │
│     ┌──────────┴────────┐   ┌─────────┴──────────┐         │
│     │   order_items     │   │ order_status_      │         │
│     │                   │   │ history            │         │
│     │ - id (PK)         │   │                    │         │
│     │ - order_id (FK)   │   │ - id (PK)          │         │
│     │ - product_id      │   │ - order_id (FK)    │         │
│     │ - product_name    │   │ - old_status       │         │
│     │ - product_sku     │   │ - new_status       │         │
│     │ - price           │   │ - comment          │         │
│     │ - quantity        │   │ - changed_by       │         │
│     │ - subtotal        │   │ - changed_at       │         │
│     └───────────────────┘   └────────────────────┘         │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Entity Styling:

1. **orders (Main Entity)**
   - Color: Light blue (#D6EAF8)
   - Border: 2px solid blue
   - Position: Center/Top

2. **order_items (Child Entity)**
   - Color: Light green (#D5F4E6)
   - Border: 2px solid green
   - Position: Bottom-left

3. **order_status_history (Audit Entity)**
   - Color: Light orange (#FAE5D3)
   - Border: 2px solid orange
   - Position: Bottom-right

---

## Order Status Flow Diagram

Include this state diagram in a separate box or on the same canvas:

```
┌─────────────────────────────────────────────────────────────┐
│                     Order Status Flow                        │
│                                                               │
│                    [PENDING]                                 │
│                        │                                     │
│                        ▼                                     │
│                   [CONFIRMED]                                │
│                        │                                     │
│                        ▼                                     │
│                  [PROCESSING]                                │
│                        │                                     │
│                        ▼                                     │
│                    [SHIPPED]                                 │
│                        │                                     │
│                        ▼                                     │
│                   [DELIVERED]                                │
│                                                               │
│   [CANCELLED] ◄──────┬────────┬──────────┐                  │
│                      │        │          │                   │
│                 (from PENDING, CONFIRMED, PROCESSING)        │
│                                                               │
│   [REFUNDED] ◄───────────────────────────────── [DELIVERED] │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Cross-Service Relationships (Logical References)

Show these with dotted lines to external entities:

```
┌──────────────┐
│ User Service │
└──────┬───────┘
       ┊ (Logical FK)
       ┊
       ▼
┌──────────────┐
│   orders     │
│ - user_id    │◄┈┈┈┈ Shipping Address (user_addresses.id)
│ - shipping_  │◄┈┈┈┈ Billing Address (user_addresses.id)
│   address_id │
│ - billing_   │
│   address_id │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ order_items  │
│ - product_id │┈┈┈┈► Product Service (products.id)
└──────────────┘
       ┊
       ▼
┌──────────────┐
│Payment Service│
│ - order_id   │
└──────────────┘
```

---

## Important Business Rules

### 1. Order Calculation
```
subtotal = Σ(order_items.subtotal)
total_amount = subtotal + tax_amount + shipping_amount - discount_amount
```

### 2. Product Snapshot
- `order_items` stores product details at time of purchase
- Even if product price changes later, order reflects original price
- Fields: product_name, product_sku, price (snapshots)

### 3. Status Transitions
All status changes are logged in `order_status_history`:
```
PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
   ↓          ↓            ↓
[CANCELLED]◄──┴────────────┘
   
DELIVERED → [REFUNDED]
```

### 4. Audit Trail
Every change to order.status creates a record in order_status_history:
- old_status: Previous status
- new_status: Current status
- changed_by: User who made the change (admin or system)
- changed_at: Timestamp
- comment: Reason for change

---

## Data Integrity Notes

### Cascade Rules:
- Delete order → Cascade delete order_items
- Delete order → Cascade delete order_status_history

### Constraints:
- order_number: UNIQUE across all orders
- quantity: CHECK (quantity > 0)
- subtotal in order_items: CHECK (subtotal = price * quantity)
- total_amount in orders: CHECK (total_amount >= 0)

---

## Indexes for Performance

```sql
-- Orders table
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_order_date ON orders(order_date DESC);
CREATE INDEX idx_orders_order_number ON orders(order_number);

-- Order items table
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Status history table
CREATE INDEX idx_order_status_history_order_id ON order_status_history(order_id);
CREATE INDEX idx_order_status_history_changed_at ON order_status_history(changed_at DESC);
```

---

## Sample Query Flows

### Get Order with Items:
```
orders (1) ──< order_items (N)
```

### Get Order History:
```
orders (1) ──< order_status_history (N)
ORDER BY changed_at DESC
```

### Get User's Orders:
```
users.id ┈┈┈┈> orders.user_id
WHERE user_id = <user_id>
ORDER BY order_date DESC
```

---

## Export Instructions

1. Create main ER diagram with 3 entities
2. Create separate status flow diagram
3. Create cross-service reference diagram
4. Export all as:
   - PNG (300 DPI for report)
   - SVG (for web documentation)
   - PDF (for presentations)

Recommended size: 1920x1080 or A4 landscape

---

## Figure Captions for Report

**Figure X.3: Order Service Entity-Relationship Diagram**

*The Order Service database schema consists of three entities: orders (main entity storing order details and status), order_items (storing individual line items with product snapshots), and order_status_history (audit trail for status changes). The schema implements a one-to-many relationship from orders to both child entities, enabling complete order tracking and historical audit capabilities.*

**Figure X.4: Order Status State Diagram**

*This state diagram illustrates the order lifecycle with seven possible states. Orders progress from PENDING through CONFIRMED, PROCESSING, SHIPPED, to DELIVERED. Cancellation is possible from PENDING, CONFIRMED, or PROCESSING states. Refunds can be initiated from DELIVERED state. All transitions are logged in the order_status_history table.*
