# Database Schema Summary - For Report

This document provides a concise summary of the database schema in the format required for the academic report.

---

## Tables Overview

### USER SERVICE DATABASE

**Tables:**
1. users
2. user_roles  
3. user_role_mapping
4. user_addresses
5. password_reset_tokens

### PRODUCT SERVICE DATABASE

**Tables:**
6. categories
7. products
8. product_images
9. product_inventory
10. product_reviews

### ORDER SERVICE DATABASE

**Tables:**
11. orders
12. order_items
13. order_status_history

### PAYMENT SERVICE DATABASE

**Tables:**
14. payment_methods
15. transactions
16. user_saved_payment_methods

### CART SERVICE DATABASE (MongoDB)

**Collections:**
17. carts

---

## Detailed Table Definitions

### 1. users
- id (UUID, Primary Key)
- email (VARCHAR(255), UNIQUE, NOT NULL)
- password (VARCHAR(255), NOT NULL)
- first_name (VARCHAR(100), NOT NULL)
- last_name (VARCHAR(100), NOT NULL)
- phone_number (VARCHAR(20), UNIQUE, NULLABLE)
- is_active (BOOLEAN, DEFAULT TRUE)
- is_verified (BOOLEAN, DEFAULT FALSE)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### 2. user_roles
- id (SERIAL, Primary Key)
- name (VARCHAR(50), UNIQUE, NOT NULL)
- description (TEXT)
- created_at (TIMESTAMP)

### 3. user_role_mapping
- id (SERIAL, Primary Key)
- user_id (UUID, Foreign Key)
- role_id (INTEGER, Foreign Key)
- assigned_at (TIMESTAMP)

### 4. user_addresses
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key)
- address_type (ENUM: 'SHIPPING', 'BILLING')
- full_name (VARCHAR(200))
- phone_number (VARCHAR(20))
- address_line1 (VARCHAR(255))
- address_line2 (VARCHAR(255))
- city (VARCHAR(100))
- state (VARCHAR(100))
- postal_code (VARCHAR(20))
- country (VARCHAR(100))
- is_default (BOOLEAN)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### 5. password_reset_tokens
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key)
- token (VARCHAR(255), UNIQUE)
- expires_at (TIMESTAMP)
- is_used (BOOLEAN)
- created_at (TIMESTAMP)

### 6. categories
- id (UUID, Primary Key)
- name (VARCHAR(100), UNIQUE)
- slug (VARCHAR(100), UNIQUE)
- description (TEXT)
- parent_id (UUID, Foreign Key)
- image_url (VARCHAR(500))
- is_active (BOOLEAN)
- display_order (INTEGER)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### 7. products
- id (UUID, Primary Key)
- category_id (UUID, Foreign Key)
- name (VARCHAR(255))
- slug (VARCHAR(255), UNIQUE)
- description (TEXT)
- short_description (VARCHAR(500))
- price (DECIMAL(10,2))
- compare_at_price (DECIMAL(10,2))
- cost_price (DECIMAL(10,2))
- sku (VARCHAR(100), UNIQUE)
- barcode (VARCHAR(100), UNIQUE)
- is_active (BOOLEAN)
- is_featured (BOOLEAN)
- weight (DECIMAL(10,2))
- dimensions (JSONB)
- meta_title (VARCHAR(255))
- meta_description (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### 8. product_images
- id (UUID, Primary Key)
- product_id (UUID, Foreign Key)
- image_url (VARCHAR(500))
- alt_text (VARCHAR(255))
- display_order (INTEGER)
- is_primary (BOOLEAN)
- created_at (TIMESTAMP)

### 9. product_inventory
- id (UUID, Primary Key)
- product_id (UUID, Foreign Key, UNIQUE)
- quantity (INTEGER)
- reserved_quantity (INTEGER)
- low_stock_threshold (INTEGER)
- allow_backorder (BOOLEAN)
- updated_at (TIMESTAMP)

### 10. product_reviews
- id (UUID, Primary Key)
- product_id (UUID, Foreign Key)
- user_id (UUID)
- rating (INTEGER)
- title (VARCHAR(255))
- comment (TEXT)
- is_verified_purchase (BOOLEAN)
- is_approved (BOOLEAN)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### 11. orders
- id (UUID, Primary Key)
- order_number (VARCHAR(50), UNIQUE)
- user_id (UUID)
- status (ENUM)
- subtotal (DECIMAL(10,2))
- tax_amount (DECIMAL(10,2))
- shipping_amount (DECIMAL(10,2))
- discount_amount (DECIMAL(10,2))
- total_amount (DECIMAL(10,2))
- currency (VARCHAR(3))
- shipping_address_id (UUID)
- billing_address_id (UUID)
- notes (TEXT)
- tracking_number (VARCHAR(100))
- shipped_at (TIMESTAMP)
- delivered_at (TIMESTAMP)
- cancelled_at (TIMESTAMP)
- cancellation_reason (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### 12. order_items
- id (UUID, Primary Key)
- order_id (UUID, Foreign Key)
- product_id (UUID)
- product_name (VARCHAR(255))
- product_sku (VARCHAR(100))
- quantity (INTEGER)
- unit_price (DECIMAL(10,2))
- total_price (DECIMAL(10,2))
- created_at (TIMESTAMP)

### 13. order_status_history
- id (UUID, Primary Key)
- order_id (UUID, Foreign Key)
- from_status (VARCHAR(50))
- to_status (VARCHAR(50))
- notes (TEXT)
- changed_by (UUID)
- created_at (TIMESTAMP)

### 14. payment_methods
- id (SERIAL, Primary Key)
- name (VARCHAR(50), UNIQUE)
- code (VARCHAR(20), UNIQUE)
- is_active (BOOLEAN)
- display_order (INTEGER)
- created_at (TIMESTAMP)

### 15. transactions
- id (UUID, Primary Key)
- transaction_number (VARCHAR(50), UNIQUE)
- order_id (UUID)
- user_id (UUID)
- payment_method_id (INTEGER, Foreign Key)
- amount (DECIMAL(10,2))
- currency (VARCHAR(3))
- status (ENUM)
- gateway_transaction_id (VARCHAR(255))
- gateway_response (JSONB)
- failure_reason (TEXT)
- processed_at (TIMESTAMP)
- refunded_at (TIMESTAMP)
- refund_amount (DECIMAL(10,2))
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### 16. user_saved_payment_methods
- id (UUID, Primary Key)
- user_id (UUID)
- payment_method_id (INTEGER, Foreign Key)
- card_last_four (VARCHAR(4))
- card_brand (VARCHAR(20))
- expiry_month (INTEGER)
- expiry_year (INTEGER)
- is_default (BOOLEAN)
- gateway_customer_id (VARCHAR(255))
- gateway_token (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### 17. carts (MongoDB Collection)
- _id (ObjectId)
- user_id (String)
- items (Array of Objects)
- subtotal (Decimal)
- tax_amount (Decimal)
- total_amount (Decimal)
- applied_coupons (Array)
- created_at (Timestamp)
- updated_at (Timestamp)
- expires_at (Timestamp)

---

## Foreign Keys

### User Service
- user_role_mapping(user_id) REFERENCES users(id) ON DELETE CASCADE
- user_role_mapping(role_id) REFERENCES user_roles(id) ON DELETE CASCADE
- user_addresses(user_id) REFERENCES users(id) ON DELETE CASCADE
- password_reset_tokens(user_id) REFERENCES users(id) ON DELETE CASCADE

### Product Service
- categories(parent_id) REFERENCES categories(id) ON DELETE SET NULL
- products(category_id) REFERENCES categories(id) ON DELETE RESTRICT
- product_images(product_id) REFERENCES products(id) ON DELETE CASCADE
- product_inventory(product_id) REFERENCES products(id) ON DELETE CASCADE
- product_reviews(product_id) REFERENCES products(id) ON DELETE CASCADE

### Order Service
- order_items(order_id) REFERENCES orders(id) ON DELETE CASCADE
- order_status_history(order_id) REFERENCES orders(id) ON DELETE CASCADE

### Payment Service
- transactions(payment_method_id) REFERENCES payment_methods(id) ON DELETE RESTRICT
- user_saved_payment_methods(payment_method_id) REFERENCES payment_methods(id) ON DELETE CASCADE

---

## Cardinality of Relations

### User Service
- Between users and user_roles → **M:N** (Many-to-Many via user_role_mapping)
- Between users and user_addresses → **1:N** (One-to-Many)
- Between users and password_reset_tokens → **1:N** (One-to-Many)

### Product Service
- Between categories and categories (parent-child) → **1:N** (One-to-Many, Self-referencing)
- Between categories and products → **1:N** (One-to-Many)
- Between products and product_images → **1:N** (One-to-Many)
- Between products and product_inventory → **1:1** (One-to-One)
- Between products and product_reviews → **1:N** (One-to-Many)

### Order Service
- Between orders and order_items → **1:N** (One-to-Many)
- Between orders and order_status_history → **1:N** (One-to-Many)

### Payment Service
- Between payment_methods and transactions → **1:N** (One-to-Many)
- Between payment_methods and user_saved_payment_methods → **1:N** (One-to-Many)

### Cross-Service References (Logical, not enforced by FK)
- Between users(id) and orders(user_id) → **1:N**
- Between users(id) and transactions(user_id) → **1:N**
- Between users(id) and product_reviews(user_id) → **1:N**
- Between users(id) and carts(user_id) → **1:1**
- Between products(id) and order_items(product_id) → **1:N**
- Between orders(id) and transactions(order_id) → **1:N**
- Between user_addresses(id) and orders(shipping_address_id) → **1:N**
- Between user_addresses(id) and orders(billing_address_id) → **1:N**

---

## Database Design Principles Applied

### 1. Normalization
- **1NF**: All tables have atomic values
- **2NF**: All non-key attributes fully depend on primary key
- **3NF**: No transitive dependencies

### 2. Denormalization (Where Needed)
- **order_items**: Stores product_name, product_sku (snapshot at order time)
- **Reason**: Product details may change, but order history must remain accurate

### 3. Indexing Strategy
- **Primary keys**: All tables
- **Foreign keys**: All relationships
- **Unique constraints**: email, sku, order_number, transaction_number
- **Query optimization**: status fields, created_at, is_active

### 4. Data Integrity
- **NOT NULL constraints**: Critical fields
- **CHECK constraints**: Valid ranges (rating 1-5, quantity > 0)
- **UNIQUE constraints**: Prevent duplicates
- **Foreign key constraints**: Referential integrity
- **ON DELETE actions**: CASCADE, RESTRICT, SET NULL

### 5. Performance Optimization
- **UUID for distributed systems**: Better for microservices
- **JSONB for flexible data**: Indexable JSON
- **Proper data types**: DECIMAL for money, TIMESTAMP for time
- **Indexes on frequently queried fields**

### 6. Scalability
- **Database per service**: Independent scaling
- **MongoDB for carts**: Fast reads/writes, flexible schema
- **Redis caching layer**: Reduce database load (to be added)
- **Elasticsearch for search**: Offload search queries (to be added)

---

## Total Tables: 17
- PostgreSQL: 16 tables across 4 service databases
- MongoDB: 1 collection

This schema supports all functional requirements from the PRD and is optimized for Django ORM implementation.
