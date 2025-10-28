# Cart Service ER Diagram

## Entity Relationship Diagram - Cart Service (MongoDB)

This document provides the structure for creating the ER diagram in draw.io.

---

## MongoDB Collection Structure

### carts (MongoDB Collection)

**Document Schema:**
```javascript
{
  _id: ObjectId,                    // MongoDB default ID
  user_id: String (UUID),           // External reference to User Service
  items: [                          // Array of cart items
    {
      product_id: String (UUID),    // External reference to Product Service
      product_name: String,         // Product snapshot
      product_image: String,        // Product snapshot (URL)
      price: Decimal128,            // Product snapshot
      quantity: Integer,            // Quantity in cart
      subtotal: Decimal128,         // Calculated (price * quantity)
      added_at: Date                // When item was added
    }
  ],
  subtotal: Decimal128,             // Sum of all item subtotals
  tax_amount: Decimal128,           // Calculated tax
  shipping_amount: Decimal128,      // Shipping charges
  discount_amount: Decimal128,      // Applied discounts
  total_amount: Decimal128,         // Final amount
  coupon_code: String,              // Applied coupon (optional)
  created_at: Date,                 // Cart creation timestamp
  updated_at: Date,                 // Last modification timestamp
  expires_at: Date                  // TTL - cart expiration (7 days)
}
```

---

## Redis Cache Structure

Cart data is cached in Redis for fast access:

### Key Pattern:
```
cart:{user_id}
```

### Value (JSON String):
```json
{
  "items": [
    {
      "product_id": "uuid",
      "product_name": "Product Name",
      "price": 999.99,
      "quantity": 2,
      "subtotal": 1999.98
    }
  ],
  "subtotal": 1999.98,
  "tax_amount": 359.99,
  "shipping_amount": 50.00,
  "discount_amount": 100.00,
  "total_amount": 2309.97
}
```

### TTL:
- Redis TTL: 1 hour (3600 seconds)
- MongoDB TTL: 7 days (604800 seconds)

---

## Draw.io Instructions

### Layout Suggestion:

Since MongoDB uses a document model (not relational), the ER diagram will look different:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cart Service                             │
│                    (MongoDB + Redis Layer)                       │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Redis Cache Layer                     │   │
│  │                                                           │   │
│  │   Key: cart:{user_id}                                    │   │
│  │   Value: JSON cart data                                  │   │
│  │   TTL: 1 hour                                            │   │
│  │                                                           │   │
│  │   [High-speed in-memory access]                          │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                       │
│                          │ Cache Miss / Persistence              │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              MongoDB Collection: carts                   │   │
│  │                                                           │   │
│  │  Document Structure:                                     │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │ _id: ObjectId                                   │   │   │
│  │  │ user_id: String (UUID) ──┬──► User Service     │   │   │
│  │  │                           │                      │   │   │
│  │  │ items: [                  │                      │   │   │
│  │  │   {                       │                      │   │   │
│  │  │     product_id ────────┬──┼──► Product Service  │   │   │
│  │  │     product_name       │  │                      │   │   │
│  │  │     product_image      │  │                      │   │   │
│  │  │     price              │  │                      │   │   │
│  │  │     quantity           │  │                      │   │   │
│  │  │     subtotal           │  │                      │   │   │
│  │  │     added_at           │  │                      │   │   │
│  │  │   }                    │  │                      │   │   │
│  │  │ ]                      │  │                      │   │   │
│  │  │                        │  │                      │   │   │
│  │  │ subtotal               │  │                      │   │   │
│  │  │ tax_amount             │  │                      │   │   │
│  │  │ shipping_amount        │  │                      │   │   │
│  │  │ discount_amount        │  │                      │   │   │
│  │  │ total_amount           │  │                      │   │   │
│  │  │ coupon_code            │  │                      │   │   │
│  │  │ created_at             │  │                      │   │   │
│  │  │ updated_at             │  │                      │   │   │
│  │  │ expires_at (TTL Index) │  │                      │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                        │  │                              │   │
│  │  Indexes:              │  │                              │   │
│  │  • user_id (Unique)    │  │                              │   │
│  │  • expires_at (TTL)    │  │                              │   │
│  │                        │  │                              │   │
│  └────────────────────────┼──┼──────────────────────────────┘   │
│                           │  │                                   │
│  External References:     │  │                                   │
│  ┌────────────────────────┘  │                                   │
│  │                           │                                   │
│  ▼                           ▼                                   │
│ [User Service]          [Product Service]                        │
│  users.id               products.id                              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Document Structure Visualization

For a clearer representation in draw.io:

```
┌─────────────────────────────────────────────────────────┐
│                MongoDB: carts Collection                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  _id: ObjectId("507f1f77bcf86cd799439011")            │
│  user_id: "123e4567-e89b-12d3-a456-426614174000"      │
│                                                         │
│  items: [                                              │
│    ┌───────────────────────────────────────────────┐  │
│    │ Embedded Document (Cart Item)                 │  │
│    ├───────────────────────────────────────────────┤  │
│    │ product_id: "uuid-123"                        │  │
│    │ product_name: "Laptop"                        │  │
│    │ product_image: "https://..."                  │  │
│    │ price: 45000.00                               │  │
│    │ quantity: 2                                    │  │
│    │ subtotal: 90000.00                            │  │
│    │ added_at: 2025-10-28T10:30:00Z               │  │
│    └───────────────────────────────────────────────┘  │
│    ┌───────────────────────────────────────────────┐  │
│    │ Embedded Document (Cart Item)                 │  │
│    ├───────────────────────────────────────────────┤  │
│    │ product_id: "uuid-456"                        │  │
│    │ product_name: "Mouse"                         │  │
│    │ product_image: "https://..."                  │  │
│    │ price: 500.00                                 │  │
│    │ quantity: 1                                    │  │
│    │ subtotal: 500.00                              │  │
│    │ added_at: 2025-10-28T11:15:00Z               │  │
│    └───────────────────────────────────────────────┘  │
│  ]                                                     │
│                                                         │
│  subtotal: 90500.00                                   │
│  tax_amount: 16290.00                                 │
│  shipping_amount: 100.00                              │
│  discount_amount: 500.00                              │
│  total_amount: 106390.00                              │
│  coupon_code: "SAVE500"                               │
│                                                         │
│  created_at: 2025-10-28T10:30:00Z                     │
│  updated_at: 2025-10-28T11:15:00Z                     │
│  expires_at: 2025-11-04T11:15:00Z                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Cart Operations Flow

Create a separate flow diagram:

```
┌──────────────────────────────────────────────────────────────┐
│                    Cart Operations Flow                       │
│                                                                │
│  [User adds item to cart]                                     │
│           │                                                    │
│           ▼                                                    │
│  ┌──────────────────┐                                        │
│  │ Check Redis Cache│                                        │
│  └────────┬─────────┘                                        │
│           │                                                    │
│     ┌─────┴─────┐                                            │
│     ▼           ▼                                            │
│  [Hit]      [Miss]                                           │
│     │           │                                            │
│     │           └──► Load from MongoDB                       │
│     │                        │                               │
│     │                        └──► Cache in Redis             │
│     │                                    │                   │
│     └────────────┬───────────────────────┘                   │
│                  ▼                                            │
│        Update cart items array                               │
│                  │                                            │
│                  ├──► Recalculate subtotal                   │
│                  ├──► Calculate tax                          │
│                  ├──► Add shipping                           │
│                  ├──► Apply discount                         │
│                  └──► Calculate total                        │
│                  │                                            │
│                  ▼                                            │
│         Save to Redis (immediate)                            │
│                  │                                            │
│                  ▼                                            │
│         Save to MongoDB (async/batch)                        │
│                  │                                            │
│                  ▼                                            │
│         Return updated cart to user                          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Cache Strategy Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    Cache Strategy                             │
│                                                                │
│  Read Operation:                                              │
│  ┌─────────┐   Check    ┌─────────┐  Miss   ┌────────────┐ │
│  │  User   │──────────► │  Redis  │───────►  │  MongoDB  │ │
│  │ Request │            │  Cache  │         │ (Fallback) │ │
│  └─────────┘            └────┬────┘         └──────┬─────┘ │
│                              │ Hit                  │        │
│                              │                      │        │
│                              └──────────────────────┘        │
│                                       │                      │
│                                       ▼                      │
│                                  [Return Data]               │
│                                                                │
│  Write Operation:                                             │
│  ┌─────────┐  Write    ┌─────────┐  Async   ┌────────────┐ │
│  │  User   │──────────► │  Redis  │────────► │  MongoDB  │ │
│  │ Request │            │ (Fast)  │  Sync    │(Persistent)│ │
│  └─────────┘            └─────────┘          └────────────┘ │
│                                                                │
│  Cache Invalidation:                                          │
│  • On checkout: Clear Redis + MongoDB                        │
│  • On TTL expire: Redis (1 hour), MongoDB (7 days)           │
│  • On user logout: Optional clear                            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Indexes in MongoDB

```javascript
// Unique index on user_id (one cart per user)
db.carts.createIndex({ "user_id": 1 }, { unique: true });

// TTL index - auto-delete after 7 days
db.carts.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });

// Optional: Index on items.product_id for queries
db.carts.createIndex({ "items.product_id": 1 });
```

---

## Business Rules

### 1. One Cart Per User
- user_id is **UNIQUE**
- Each user can have only one active cart
- When user logs out, cart persists (expires after 7 days)

### 2. Product Snapshot
- Store product name, image, price at time of adding
- If product price changes, cart still shows old price
- On checkout, validate against current product price

### 3. Quantity Validation
```javascript
// Before adding item
if (quantity > product_inventory.quantity - product_inventory.reserved_quantity) {
  throw new Error("Insufficient stock");
}
```

### 4. Calculation Logic
```javascript
subtotal = Σ(item.subtotal for all items)
tax_amount = subtotal * 0.18  // 18% GST
shipping_amount = 50 if subtotal < 500 else 0
discount_amount = apply_coupon(coupon_code)
total_amount = subtotal + tax_amount + shipping_amount - discount_amount
```

### 5. TTL (Time To Live)
- **Redis TTL:** 1 hour (frequent cache refresh)
- **MongoDB TTL:** 7 days (abandoned cart recovery)
- On activity: Reset `expires_at` to current_time + 7 days

---

## Cross-Service Communication

### With Product Service:
```
Cart Service ──GET──► Product Service
                      (product details, price, inventory)
                      
Cart Service ──POST─► Product Service
                      (reserve inventory on checkout)
```

### With Order Service:
```
Cart Service ──POST─► Order Service
                      (convert cart to order)
                      
Order Service ──DELETE─► Cart Service
                          (clear cart after order creation)
```

---

## Data Migration Notes

Since MongoDB is schema-less, versioning the document structure:

```javascript
{
  _id: ObjectId,
  schema_version: 1,  // For future migrations
  user_id: String,
  items: [...],
  // ... rest of fields
}
```

---

## Figure Captions for Report

**Figure X.7: Cart Service Architecture Diagram**

*The Cart Service uses MongoDB for flexible document storage and Redis for high-speed caching. The architecture shows a two-tier data strategy: Redis provides sub-millisecond read/write access with a 1-hour TTL, while MongoDB ensures persistence with a 7-day TTL for abandoned cart recovery. Each user has a single cart document containing an embedded array of cart items with product snapshots.*

**Figure X.8: Cart Operations Flow Diagram**

*This flow diagram illustrates the cart modification process. When a user adds an item, the service first checks Redis cache. On cache hit, data is immediately available; on cache miss, data is loaded from MongoDB and cached. The cart calculations (subtotal, tax, shipping, discount, total) are performed, and the updated cart is saved to both Redis (synchronously) and MongoDB (asynchronously) before returning to the user.*

**Figure X.9: Cache Strategy Diagram**

*The caching strategy implements a write-through cache pattern with Redis as the primary read layer and MongoDB as the persistent store. Read operations prioritize Redis for speed, falling back to MongoDB on cache miss. Write operations update Redis immediately for fast response while asynchronously syncing to MongoDB for durability. Cache invalidation occurs on checkout, TTL expiration, or explicit user action.*

---

## Export Instructions

1. Create main architecture diagram (MongoDB + Redis layers)
2. Create document structure visualization
3. Create cart operations flow diagram
4. Create cache strategy diagram
5. Export all as:
   - PNG (300 DPI for report)
   - SVG (for documentation)
   - PDF (for presentations)

Recommended size: 1920x1080 or A4 landscape

---

## Color Coding for Draw.io

- **Redis Layer:** Light red (#FADBD8) - Fast cache
- **MongoDB Layer:** Light green (#D5F4E6) - Persistent storage
- **Embedded Documents:** Light purple (#E8DAEF) - Nested items
- **External References:** Light yellow (#FEF9E7) - User/Product services
- **Flow Arrows:** Blue for reads, Green for writes
