# Product Service ER Diagram

## Entity Relationship Diagram - Product Service

This document provides the structure for creating the ER diagram in draw.io.

---

## Entities and Attributes

### 1. categories (Hierarchical Entity)
**Attributes:**
- 🔑 id (PK) - UUID
- 📝 name (UNIQUE) - VARCHAR(100)
- 🔗 slug (UNIQUE) - VARCHAR(100)
- 📝 description - TEXT
- 🔗 parent_id (FK) - UUID → categories.id (Self-referencing)
- 🖼️ image_url - VARCHAR(500)
- ✓ is_active - BOOLEAN
- 🔢 display_order - INTEGER
- 📅 created_at - TIMESTAMP
- 📅 updated_at - TIMESTAMP

### 2. products (Main Entity)
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 category_id (FK) - UUID → categories.id
- 📝 name - VARCHAR(255)
- 🔗 slug (UNIQUE) - VARCHAR(255)
- 📝 description - TEXT
- 📝 short_description - VARCHAR(500)
- 💰 price - DECIMAL(10,2)
- 💰 compare_at_price - DECIMAL(10,2)
- 💰 cost_price - DECIMAL(10,2)
- 📦 sku (UNIQUE) - VARCHAR(100)
- 📱 barcode (UNIQUE) - VARCHAR(100)
- ✓ is_active - BOOLEAN
- ⭐ is_featured - BOOLEAN
- ⚖️ weight - DECIMAL(10,2)
- 📐 dimensions - JSONB
- 🔍 meta_title - VARCHAR(255)
- 🔍 meta_description - TEXT
- 📅 created_at - TIMESTAMP
- 📅 updated_at - TIMESTAMP

### 3. product_images
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 product_id (FK) - UUID → products.id
- 🖼️ image_url - VARCHAR(500)
- 📝 alt_text - VARCHAR(255)
- 🔢 display_order - INTEGER
- ✓ is_primary - BOOLEAN
- 📅 created_at - TIMESTAMP

### 4. product_inventory
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 product_id (FK, UNIQUE) - UUID → products.id
- 📦 quantity - INTEGER
- 📦 reserved_quantity - INTEGER
- 🔔 low_stock_threshold - INTEGER
- ✓ allow_backorder - BOOLEAN
- 📅 updated_at - TIMESTAMP

### 5. product_reviews
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 product_id (FK) - UUID → products.id
- 🔗 user_id - UUID (External reference to User Service)
- ⭐ rating - INTEGER (1-5)
- 📝 title - VARCHAR(255)
- 📝 comment - TEXT
- ✓ is_verified_purchase - BOOLEAN
- ✓ is_approved - BOOLEAN
- 📅 created_at - TIMESTAMP
- 📅 updated_at - TIMESTAMP

---

## Relationships

### 1. categories → categories (One-to-Many, Self-referencing)
```
categories ──────|──────< categories
(parent)     1          N   (children)
```
- **Cardinality:** 1:N
- **Relationship:** Parent category can have multiple child categories (hierarchy)
- **Foreign Key:** categories.parent_id → categories.id
- **ON DELETE:** SET NULL

### 2. categories → products (One-to-Many)
```
categories ──────|──────< products
     1                  N
```
- **Cardinality:** 1:N
- **Relationship:** One category contains many products
- **Foreign Key:** products.category_id → categories.id
- **ON DELETE:** RESTRICT

### 3. products → product_images (One-to-Many)
```
products ──────|──────< product_images
    1                 N
```
- **Cardinality:** 1:N
- **Relationship:** One product can have multiple images
- **Foreign Key:** product_images.product_id → products.id
- **ON DELETE:** CASCADE

### 4. products ↔ product_inventory (One-to-One)
```
products ──────|──────| product_inventory
    1                 1
```
- **Cardinality:** 1:1
- **Relationship:** One product has exactly one inventory record
- **Foreign Key:** product_inventory.product_id → products.id (UNIQUE)
- **ON DELETE:** CASCADE

### 5. products → product_reviews (One-to-Many)
```
products ──────|──────< product_reviews
    1                 N
```
- **Cardinality:** 1:N
- **Relationship:** One product can have many reviews
- **Foreign Key:** product_reviews.product_id → products.id
- **ON DELETE:** CASCADE

---

## Draw.io Instructions

### Layout Suggestion:
```
┌────────────────────────────────────────────────────────────────┐
│                                                                  │
│        ┌──────────────┐                                        │
│    ┌───┤  categories  │◄───┐ (Self-referencing)               │
│    │   │              │    │                                    │
│    │   │ - id (PK)    │    │                                    │
│    │   │ - name       │    │                                    │
│    │   │ - slug       │    │                                    │
│    │   │ - parent_id(FK)───┘                                   │
│    │   │ - image_url  │                                         │
│    │   │ - is_active  │                                         │
│    │   │ - display_order                                        │
│    │   └──────┬───────┘                                         │
│    │          │ 1                                               │
│    │          │                                                 │
│    │   ┌──────┴───────────────────┐                            │
│    │   │ N                         │                            │
│    │   │      ┌──────────────┐    │                            │
│    │   │      │   products   │    │                            │
│    │   │      │  (Central)   │    │                            │
│    │   │      │              │    │                            │
│    │   │      │ - id (PK)    │    │                            │
│    │   │      │ - category_id(FK)─┘                            │
│    │   │      │ - name       │                                 │
│    │   │      │ - slug       │                                 │
│    │   │      │ - description│                                 │
│    │   │      │ - price      │                                 │
│    │   │      │ - sku        │                                 │
│    │   │      │ - is_active  │                                 │
│    │   │      │ - is_featured│                                 │
│    │   │      └──────┬───────┘                                 │
│    │                 │ 1                                        │
│    │          ┌──────┼────────┬─────────┐                      │
│    │          │      │        │         │                      │
│    │        N │    1 │ 1    N │       N │                      │
│    │          │      │        │         │                      │
│    │  ┌───────┴──┐ ┌┴────────┴──┐  ┌───┴──────────┐          │
│    │  │ product_ │ │  product_  │  │   product_   │          │
│    │  │ images   │ │ inventory  │  │   reviews    │          │
│    │  │          │ │            │  │              │          │
│    │  │-id (PK)  │ │-id (PK)    │  │-id (PK)      │          │
│    │  │-product_ │ │-product_id │  │-product_id   │          │
│    │  │ id (FK)  │ │  (FK,UNIQUE)  │ (FK)         │          │
│    │  │-image_url│ │-quantity   │  │-user_id      │          │
│    │  │-alt_text │ │-reserved_  │  │-rating       │          │
│    │  │-display_ │ │ quantity   │  │-title        │          │
│    │  │ order    │ │-low_stock_ │  │-comment      │          │
│    │  │-is_primary│ │ threshold │  │-is_approved  │          │
│    │  └──────────┘ └────────────┘  └──────────────┘          │
│    │                                                            │
└────┴────────────────────────────────────────────────────────────┘
```

### Steps to Create in Draw.io:

1. **Create Main Entity (products)**
   - Center of the diagram
   - Light blue background
   - Bold header

2. **Create Parent Entity (categories)**
   - Top of diagram
   - Light yellow background
   - Show self-referencing arrow

3. **Create Child Entities**
   - Below products
   - Different colors for each
   - product_images: Light purple
   - product_inventory: Light green
   - product_reviews: Light orange

4. **Add Relationships**
   - Self-referencing arrow for categories
   - One-to-many from categories to products
   - One-to-one from products to inventory (both ends with single line)
   - One-to-many from products to images
   - One-to-many from products to reviews

---

## Crow's Foot Notation Examples

### One-to-Many:
```
categories ──────|──────< products
```

### One-to-One:
```
products ──────|──────| product_inventory
```

### Self-referencing:
```
        ┌────────────┐
        │            │
     ┌──┤categories  │
     │  │            │
     │  │-parent_id──┘
     │  └────────────┘
     └────── 1:N
```

---

## Special Considerations

### 1. Category Hierarchy
The self-referencing relationship in categories allows:
- Top-level categories (parent_id = NULL)
- Sub-categories (parent_id references another category)
- Unlimited depth (though 3 levels recommended)

Example:
```
Electronics (parent_id = NULL)
├── Laptops (parent_id = Electronics.id)
│   ├── Gaming Laptops (parent_id = Laptops.id)
│   └── Business Laptops (parent_id = Laptops.id)
└── Smartphones (parent_id = Electronics.id)
```

### 2. Product Images
- Multiple images per product
- One marked as `is_primary`
- Ordered by `display_order`

### 3. Inventory Tracking
- One-to-one relationship ensures single inventory record
- `quantity` = available stock
- `reserved_quantity` = items in pending orders
- Available = quantity - reserved_quantity

---

## Cross-Service Relationships (Logical References)

```
products.id ┈┈┈┈> order_items.product_id (Order Service)
products.id ┈┈┈┈> carts.items.product_id (Cart Service)

product_reviews.user_id ┈┈┈┈> users.id (User Service)
```

---

## Elasticsearch Integration

Product data is synced to Elasticsearch for search:

```
products (PostgreSQL) ──→ Sync ──→ products_index (Elasticsearch)
```

Fields indexed:
- name (full-text)
- description (full-text)
- category_name
- price
- sku
- is_active

---

## Export Instructions

Save as:
- PNG: For report inclusion
- SVG: For scalable documentation
- PDF: For presentations

Recommended dimensions: 1920x1200

---

## Figure Caption for Report

**Figure X.2: Product Service Entity-Relationship Diagram**

*This diagram shows the Product Service database schema with five interconnected entities. The categories table features a self-referencing relationship for hierarchical category structure. The products entity serves as the central table with one-to-many relationships to product_images and product_reviews, and a one-to-one relationship with product_inventory for stock management. The schema supports full product catalog management including categorization, multi-image support, inventory tracking, and customer reviews.*
