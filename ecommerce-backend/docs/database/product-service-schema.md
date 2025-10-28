# Product Service Database Schema

## Database: product_service_db (PostgreSQL)

This database handles product catalog, categories, inventory, and reviews.

---

## Tables

### 1. categories
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

**Django Model Considerations:**
- Use `SlugField` for auto-generation from name
- ForeignKey to self for parent_id (`related_name='children'`)
- Use MPTT (Modified Preorder Tree Traversal) library for efficient hierarchy queries

---

### 2. products
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

**Django Model Considerations:**
- Use `DecimalField` for all money fields
- Use `JSONField` for dimensions
- Auto-generate slug from name
- Use `django-money` for currency handling

---

### 3. product_images
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

**Django Model Considerations:**
- ForeignKey with `related_name='images'`
- Order by `display_order`
- Ensure only one `is_primary=True` per product

---

### 4. product_inventory
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

**Django Model Considerations:**
- OneToOneField with `related_name='inventory'`
- Add method: `available_quantity = quantity - reserved_quantity`
- Signal to send alert when quantity <= low_stock_threshold

---

### 5. product_reviews
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

**Django Model Considerations:**
- Use `IntegerChoices` for rating (1-5)
- Add average rating calculation on Product model
- Only allow one review per user per product

---

## Relationships

### categories → categories (One-to-Many, Self-referencing)
- Parent category → Child categories (hierarchy)
- **Cardinality: 1:N**

### categories → products (One-to-Many)
- One category has many products
- One product belongs to one category
- **Cardinality: 1:N**

### products → product_images (One-to-Many)
- One product has multiple images
- One image belongs to one product
- **Cardinality: 1:N**

### products ↔ product_inventory (One-to-One)
- One product has one inventory record
- One inventory record for one product
- **Cardinality: 1:1**

### products → product_reviews (One-to-Many)
- One product has many reviews
- One review belongs to one product
- **Cardinality: 1:N**

---

## Foreign Keys Summary

- `categories(parent_id)` REFERENCES `categories(id)` ON DELETE SET NULL
- `products(category_id)` REFERENCES `categories(id)` ON DELETE RESTRICT
- `product_images(product_id)` REFERENCES `products(id)` ON DELETE CASCADE
- `product_inventory(product_id)` REFERENCES `products(id)` ON DELETE CASCADE
- `product_reviews(product_id)` REFERENCES `products(id)` ON DELETE CASCADE

---

## Cross-Service References (Logical)

The `products.id` is referenced by other services:
- Order Service: `order_items.product_id`
- Cart Service: `carts.items.product_id`

These are **logical references** only.

---

## Elasticsearch Integration

Products will be synced to Elasticsearch for fast search:

**Index: products**
```json
{
  "id": "uuid",
  "name": "string",
  "description": "text",
  "category_name": "string",
  "price": "float",
  "sku": "string",
  "is_active": "boolean",
  "images": ["url1", "url2"]
}
```

**Search Fields:**
- Full-text search on: name, description
- Filters: category, price range, rating
- Sorting: price, created_at, popularity

---

## APIs That Will Use This Schema

- GET `/api/products` - List products (with filters)
- GET `/api/products/:id` - Get product details
- POST `/api/products` - Create product (Admin)
- PUT `/api/products/:id` - Update product (Admin)
- DELETE `/api/products/:id` - Delete product (Admin)
- GET `/api/categories` - List categories
- GET `/api/products/search` - Search products
- POST `/api/products/:id/reviews` - Add review
- GET `/api/products/:id/reviews` - Get product reviews

---

## Sample Data

### categories
```sql
INSERT INTO categories (id, name, slug, parent_id, is_active)
VALUES 
  ('cat-1', 'Electronics', 'electronics', NULL, TRUE),
  ('cat-2', 'Laptops', 'laptops', 'cat-1', TRUE),
  ('cat-3', 'Smartphones', 'smartphones', 'cat-1', TRUE);
```

### products
```sql
INSERT INTO products (id, category_id, name, slug, description, price, sku, is_active)
VALUES 
  ('prod-1', 'cat-2', 'MacBook Pro 16"', 'macbook-pro-16', 'Powerful laptop for professionals', 2499.99, 'MBP-16-001', TRUE),
  ('prod-2', 'cat-3', 'iPhone 15 Pro', 'iphone-15-pro', 'Latest iPhone with A17 chip', 999.99, 'IPH-15P-001', TRUE);
```
