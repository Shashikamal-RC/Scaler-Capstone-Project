# E-commerce Database Schema Design

## Overview
This document describes the complete database schema for the e-commerce backend microservices architecture.

---

## Database Distribution

### PostgreSQL Databases (Relational Data)
- **User Service Database** - User accounts, authentication, roles
- **Product Service Database** - Products, categories, inventory
- **Order Service Database** - Orders, order items, order history
- **Payment Service Database** - Transactions, payment methods

### MongoDB Database (Document-based)
- **Cart Service Database** - Shopping carts (flexible schema)

---

## 1. USER SERVICE DATABASE (PostgreSQL)

### Table: users
Stores user account information.

**Fields:**
- `id` (UUID, Primary Key) - Unique user identifier
- `email` (VARCHAR(255), UNIQUE, NOT NULL) - User email (used for login)
- `password` (VARCHAR(255), NOT NULL) - Hashed password
- `first_name` (VARCHAR(100), NOT NULL) - First name
- `last_name` (VARCHAR(100), NOT NULL) - Last name
- `phone_number` (VARCHAR(20), UNIQUE, NULLABLE) - Contact number
- `is_active` (BOOLEAN, DEFAULT TRUE) - Account active status
- `is_verified` (BOOLEAN, DEFAULT FALSE) - Email verification status
- `created_at` (TIMESTAMP, DEFAULT NOW()) - Account creation time
- `updated_at` (TIMESTAMP, AUTO UPDATE) - Last update time

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`
- INDEX on `phone_number`

---

### Table: user_roles
Defines user roles (Customer, Admin, etc.).

**Fields:**
- `id` (SERIAL, Primary Key) - Role ID
- `name` (VARCHAR(50), UNIQUE, NOT NULL) - Role name (CUSTOMER, ADMIN, MANAGER)
- `description` (TEXT, NULLABLE) - Role description
- `created_at` (TIMESTAMP, DEFAULT NOW())

**Default Roles:**
- CUSTOMER - Regular user
- ADMIN - Administrator
- MANAGER - Manager (optional)

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `name`

---

### Table: user_role_mapping
Maps users to their roles (Many-to-Many).

**Fields:**
- `id` (SERIAL, Primary Key)
- `user_id` (UUID, Foreign Key -> users.id, NOT NULL)
- `role_id` (INTEGER, Foreign Key -> user_roles.id, NOT NULL)
- `assigned_at` (TIMESTAMP, DEFAULT NOW())

**Constraints:**
- FOREIGN KEY `user_id` REFERENCES `users(id)` ON DELETE CASCADE
- FOREIGN KEY `role_id` REFERENCES `user_roles(id)` ON DELETE CASCADE
- UNIQUE constraint on (`user_id`, `role_id`) - Prevent duplicate assignments

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `user_id`
- INDEX on `role_id`

---

### Table: user_addresses
Stores user delivery/billing addresses.

**Fields:**
- `id` (UUID, Primary Key) - Address ID
- `user_id` (UUID, Foreign Key -> users.id, NOT NULL)
- `address_type` (ENUM: 'SHIPPING', 'BILLING', NOT NULL)
- `full_name` (VARCHAR(200), NOT NULL) - Recipient name
- `phone_number` (VARCHAR(20), NOT NULL)
- `address_line1` (VARCHAR(255), NOT NULL)
- `address_line2` (VARCHAR(255), NULLABLE)
- `city` (VARCHAR(100), NOT NULL)
- `state` (VARCHAR(100), NOT NULL)
- `postal_code` (VARCHAR(20), NOT NULL)
- `country` (VARCHAR(100), NOT NULL)
- `is_default` (BOOLEAN, DEFAULT FALSE)
- `created_at` (TIMESTAMP, DEFAULT NOW())
- `updated_at` (TIMESTAMP, AUTO UPDATE)

**Constraints:**
- FOREIGN KEY `user_id` REFERENCES `users(id)` ON DELETE CASCADE

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `user_id`

---

### Table: password_reset_tokens
Temporary tokens for password reset.

**Fields:**
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key -> users.id, NOT NULL)
- `token` (VARCHAR(255), UNIQUE, NOT NULL) - Reset token
- `expires_at` (TIMESTAMP, NOT NULL) - Token expiration
- `is_used` (BOOLEAN, DEFAULT FALSE)
- `created_at` (TIMESTAMP, DEFAULT NOW())

**Constraints:**
- FOREIGN KEY `user_id` REFERENCES `users(id)` ON DELETE CASCADE

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `token`
- INDEX on `user_id`

---

## 2. PRODUCT SERVICE DATABASE (PostgreSQL)

### Table: categories
Product categories hierarchy.

**Fields:**
- `id` (UUID, Primary Key) - Category ID
- `name` (VARCHAR(100), UNIQUE, NOT NULL) - Category name
- `slug` (VARCHAR(100), UNIQUE, NOT NULL) - URL-friendly name
- `description` (TEXT, NULLABLE) - Category description
- `parent_id` (UUID, Foreign Key -> categories.id, NULLABLE) - Parent category (for hierarchy)
- `image_url` (VARCHAR(500), NULLABLE) - Category image
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `display_order` (INTEGER, DEFAULT 0) - Sort order
- `created_at` (TIMESTAMP, DEFAULT NOW())
- `updated_at` (TIMESTAMP, AUTO UPDATE)

**Constraints:**
- FOREIGN KEY `parent_id` REFERENCES `categories(id)` ON DELETE SET NULL
- Self-referencing for category hierarchy

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `slug`
- INDEX on `parent_id`

---

### Table: products
Product catalog.

**Fields:**
- `id` (UUID, Primary Key) - Product ID
- `category_id` (UUID, Foreign Key -> categories.id, NOT NULL)
- `name` (VARCHAR(255), NOT NULL) - Product name
- `slug` (VARCHAR(255), UNIQUE, NOT NULL) - URL-friendly name
- `description` (TEXT, NOT NULL) - Product description
- `short_description` (VARCHAR(500), NULLABLE) - Brief description
- `price` (DECIMAL(10,2), NOT NULL) - Product price
- `compare_at_price` (DECIMAL(10,2), NULLABLE) - Original price (for discounts)
- `cost_price` (DECIMAL(10,2), NULLABLE) - Cost price (internal)
- `sku` (VARCHAR(100), UNIQUE, NOT NULL) - Stock Keeping Unit
- `barcode` (VARCHAR(100), UNIQUE, NULLABLE) - Product barcode
- `is_active` (BOOLEAN, DEFAULT TRUE) - Product visibility
- `is_featured` (BOOLEAN, DEFAULT FALSE) - Featured product
- `weight` (DECIMAL(10,2), NULLABLE) - Weight in kg
- `dimensions` (JSONB, NULLABLE) - {length, width, height}
- `meta_title` (VARCHAR(255), NULLABLE) - SEO title
- `meta_description` (TEXT, NULLABLE) - SEO description
- `created_at` (TIMESTAMP, DEFAULT NOW())
- `updated_at` (TIMESTAMP, AUTO UPDATE)

**Constraints:**
- FOREIGN KEY `category_id` REFERENCES `categories(id)` ON DELETE RESTRICT

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `slug`
- UNIQUE INDEX on `sku`
- INDEX on `category_id`
- INDEX on `is_active`
- INDEX on `is_featured`

---

### Table: product_images
Product images (one product can have multiple images).

**Fields:**
- `id` (UUID, Primary Key)
- `product_id` (UUID, Foreign Key -> products.id, NOT NULL)
- `image_url` (VARCHAR(500), NOT NULL) - Image URL
- `alt_text` (VARCHAR(255), NULLABLE) - Image alt text
- `display_order` (INTEGER, DEFAULT 0) - Image order
- `is_primary` (BOOLEAN, DEFAULT FALSE) - Main product image
- `created_at` (TIMESTAMP, DEFAULT NOW())

**Constraints:**
- FOREIGN KEY `product_id` REFERENCES `products(id)` ON DELETE CASCADE

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `product_id`

---

### Table: product_inventory
Product stock/inventory management.

**Fields:**
- `id` (UUID, Primary Key)
- `product_id` (UUID, Foreign Key -> products.id, UNIQUE, NOT NULL)
- `quantity` (INTEGER, DEFAULT 0, NOT NULL) - Available quantity
- `reserved_quantity` (INTEGER, DEFAULT 0) - Reserved for pending orders
- `low_stock_threshold` (INTEGER, DEFAULT 10) - Alert threshold
- `allow_backorder` (BOOLEAN, DEFAULT FALSE)
- `updated_at` (TIMESTAMP, AUTO UPDATE)

**Constraints:**
- FOREIGN KEY `product_id` REFERENCES `products(id)` ON DELETE CASCADE
- CHECK constraint: `quantity >= 0`
- CHECK constraint: `reserved_quantity >= 0`

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `product_id`

---

### Table: product_reviews
Customer product reviews.

**Fields:**
- `id` (UUID, Primary Key)
- `product_id` (UUID, Foreign Key -> products.id, NOT NULL)
- `user_id` (UUID, NOT NULL) - References users.id (from User Service)
- `rating` (INTEGER, NOT NULL) - Rating 1-5
- `title` (VARCHAR(255), NULLABLE)
- `comment` (TEXT, NULLABLE)
- `is_verified_purchase` (BOOLEAN, DEFAULT FALSE)
- `is_approved` (BOOLEAN, DEFAULT FALSE) - Admin approval
- `created_at` (TIMESTAMP, DEFAULT NOW())
- `updated_at` (TIMESTAMP, AUTO UPDATE)

**Constraints:**
- FOREIGN KEY `product_id` REFERENCES `products(id)` ON DELETE CASCADE
- CHECK constraint: `rating BETWEEN 1 AND 5`

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `product_id`
- INDEX on `user_id`

---

## 3. ORDER SERVICE DATABASE (PostgreSQL)

### Table: orders
Customer orders.

**Fields:**
- `id` (UUID, Primary Key) - Order ID
- `order_number` (VARCHAR(50), UNIQUE, NOT NULL) - Human-readable order number
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

---

### Table: order_items
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

---

### Table: order_status_history
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

---

## 4. PAYMENT SERVICE DATABASE (PostgreSQL)

### Table: payment_methods
Available payment methods.

**Fields:**
- `id` (SERIAL, Primary Key)
- `name` (VARCHAR(50), UNIQUE, NOT NULL) - Method name
- `code` (VARCHAR(20), UNIQUE, NOT NULL) - Method code
  - Values: 'CREDIT_CARD', 'DEBIT_CARD', 'UPI', 'NET_BANKING', 'WALLET'
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `display_order` (INTEGER, DEFAULT 0)
- `created_at` (TIMESTAMP, DEFAULT NOW())

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `code`

---

### Table: transactions
Payment transactions.

**Fields:**
- `id` (UUID, Primary Key) - Transaction ID
- `transaction_number` (VARCHAR(50), UNIQUE, NOT NULL) - Readable transaction number
- `order_id` (UUID, NOT NULL) - References orders.id (from Order Service)
- `user_id` (UUID, NOT NULL) - References users.id (from User Service)
- `payment_method_id` (INTEGER, Foreign Key -> payment_methods.id, NOT NULL)
- `amount` (DECIMAL(10,2), NOT NULL)
- `currency` (VARCHAR(3), DEFAULT 'USD')
- `status` (ENUM, NOT NULL)
  - Values: 'PENDING', 'PROCESSING', 'SUCCESS', 'FAILED', 'REFUNDED', 'CANCELLED'
- `gateway_transaction_id` (VARCHAR(255), NULLABLE) - External gateway ID
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

---

### Table: user_saved_payment_methods
User's saved payment methods for quick checkout.

**Fields:**
- `id` (UUID, Primary Key)
- `user_id` (UUID, NOT NULL) - References users.id
- `payment_method_id` (INTEGER, Foreign Key -> payment_methods.id, NOT NULL)
- `card_last_four` (VARCHAR(4), NULLABLE) - Last 4 digits of card
- `card_brand` (VARCHAR(20), NULLABLE) - VISA, MASTERCARD, etc.
- `expiry_month` (INTEGER, NULLABLE)
- `expiry_year` (INTEGER, NULLABLE)
- `is_default` (BOOLEAN, DEFAULT FALSE)
- `gateway_customer_id` (VARCHAR(255), NULLABLE) - Gateway customer ID
- `gateway_token` (TEXT, NULLABLE) - Encrypted token
- `created_at` (TIMESTAMP, DEFAULT NOW())
- `updated_at` (TIMESTAMP, AUTO UPDATE)

**Constraints:**
- FOREIGN KEY `payment_method_id` REFERENCES `payment_methods(id)` ON DELETE CASCADE

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `user_id`

---

## 5. CART SERVICE DATABASE (MongoDB)

### Collection: carts
Shopping cart documents (NoSQL for flexibility).

**Document Structure:**
```json
{
  "_id": "ObjectId",
  "user_id": "UUID string",
  "items": [
    {
      "product_id": "UUID string",
      "product_name": "string",
      "product_slug": "string",
      "quantity": "integer",
      "unit_price": "decimal",
      "total_price": "decimal",
      "image_url": "string",
      "added_at": "timestamp"
    }
  ],
  "subtotal": "decimal",
  "tax_amount": "decimal",
  "total_amount": "decimal",
  "applied_coupons": [
    {
      "coupon_code": "string",
      "discount_amount": "decimal"
    }
  ],
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "expires_at": "timestamp"
}
```

**Indexes:**
- Index on `user_id` (unique)
- Index on `expires_at` (for TTL cleanup)
- Index on `items.product_id`

**TTL Index:**
- MongoDB TTL index on `expires_at` to auto-delete expired carts

---

## Relationships & Cardinality

### User Service
- **users ↔ user_roles** (Many-to-Many via user_role_mapping)
  - One user can have multiple roles
  - One role can belong to multiple users
  
- **users → user_addresses** (One-to-Many)
  - One user can have multiple addresses
  - One address belongs to one user

- **users → password_reset_tokens** (One-to-Many)
  - One user can have multiple reset tokens
  - One token belongs to one user

### Product Service
- **categories → categories** (One-to-Many, Self-referencing)
  - Parent category → Child categories (hierarchy)
  
- **categories → products** (One-to-Many)
  - One category has many products
  - One product belongs to one category

- **products → product_images** (One-to-Many)
  - One product has multiple images
  - One image belongs to one product

- **products ↔ product_inventory** (One-to-One)
  - One product has one inventory record
  - One inventory record for one product

- **products → product_reviews** (One-to-Many)
  - One product has many reviews
  - One review belongs to one product

### Order Service
- **orders → order_items** (One-to-Many)
  - One order contains multiple items
  - One item belongs to one order

- **orders → order_status_history** (One-to-Many)
  - One order has multiple status changes
  - One status change belongs to one order

### Payment Service
- **payment_methods → transactions** (One-to-Many)
  - One payment method used in many transactions
  - One transaction uses one payment method

- **payment_methods → user_saved_payment_methods** (One-to-Many)
  - One payment method type saved multiple times by users
  - One saved method is of one payment method type

### Cross-Service Relationships (via IDs)
- **users.id** referenced in: orders, transactions, product_reviews, carts
- **products.id** referenced in: order_items, carts
- **orders.id** referenced in: transactions

---

## Data Types Guide (PostgreSQL)

- **UUID** - Universally unique identifier (128-bit)
- **VARCHAR(n)** - Variable character string, max length n
- **TEXT** - Variable unlimited length text
- **INTEGER** - 4-byte integer
- **SERIAL** - Auto-incrementing integer
- **DECIMAL(p,s)** - Exact numeric, p=precision, s=scale
- **BOOLEAN** - True/false
- **TIMESTAMP** - Date and time
- **JSONB** - Binary JSON (indexable)
- **ENUM** - Enumerated type (predefined values)

---

## Indexes Strategy

### Primary Indexes
- All tables have PRIMARY KEY on `id`

### Unique Indexes
- Email, phone (users)
- SKU, slug (products)
- Order number, transaction number

### Foreign Key Indexes
- All foreign key columns are indexed for join performance

### Query Optimization Indexes
- `created_at` for time-based queries
- `status` fields for filtering
- `is_active` for active records filtering

---

## Django Model Considerations

### Built-in Django Features to Use:
1. **AbstractBaseUser** for users table (provides password hashing)
2. **UUIDField** for primary keys (better for distributed systems)
3. **JSONField** for flexible data (dimensions, gateway_response)
4. **DateTimeField** with auto_now/auto_now_add
5. **DecimalField** for money (avoid floating point errors)
6. **Choices** for ENUM fields (status, payment methods)
7. **ForeignKey** with on_delete behavior
8. **ManyToManyField** for user-roles relationship

### Django Model Managers
- Custom managers for active records filtering
- Soft delete implementation (is_deleted flag)

---

This schema is designed to be:
✅ **Normalized** - Minimal redundancy
✅ **Scalable** - Can handle growth
✅ **Performant** - Proper indexing
✅ **Django-friendly** - Aligns with Django ORM
✅ **Microservices-ready** - Database per service
