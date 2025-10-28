# Cart Service Database Schema

## Database: cart_service_db (MongoDB)

This database uses MongoDB for flexible cart structure and fast read/write operations.

---

## Collection: carts

Shopping cart documents stored in NoSQL format for maximum flexibility.

### Why MongoDB for Carts?

1. **Flexible Schema** - Cart items can have varying attributes
2. **Fast Reads/Writes** - In-memory caching with Redis
3. **Embedded Documents** - Items array embedded in cart document
4. **TTL Support** - Auto-delete expired carts
5. **No Joins Needed** - All cart data in one document

---

## Document Structure

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": [
    {
      "product_id": "prod-550e8400-e29b-41d4-a716-446655440001",
      "product_name": "MacBook Pro 16\"",
      "product_slug": "macbook-pro-16",
      "product_sku": "MBP-16-001",
      "quantity": 1,
      "unit_price": 2499.99,
      "total_price": 2499.99,
      "image_url": "https://cdn.example.com/images/macbook-pro-16.jpg",
      "is_available": true,
      "added_at": ISODate("2024-10-27T10:30:00Z")
    },
    {
      "product_id": "prod-550e8400-e29b-41d4-a716-446655440002",
      "product_name": "iPhone 15 Pro",
      "product_slug": "iphone-15-pro",
      "product_sku": "IPH-15P-001",
      "quantity": 2,
      "unit_price": 999.99,
      "total_price": 1999.98,
      "image_url": "https://cdn.example.com/images/iphone-15-pro.jpg",
      "is_available": true,
      "added_at": ISODate("2024-10-27T11:45:00Z")
    }
  ],
  "subtotal": 4499.97,
  "tax_amount": 449.99,
  "shipping_amount": 10.00,
  "discount_amount": 0.00,
  "total_amount": 4959.96,
  "applied_coupons": [],
  "created_at": ISODate("2024-10-27T10:30:00Z"),
  "updated_at": ISODate("2024-10-27T11:45:00Z"),
  "expires_at": ISODate("2024-11-03T11:45:00Z")
}
```

---

## Field Definitions

### Root Level Fields

- `_id` (ObjectId) - MongoDB unique identifier
- `user_id` (String) - References users.id from User Service
- `items` (Array) - Array of cart items (embedded documents)
- `subtotal` (Decimal128) - Sum of all item total_prices
- `tax_amount` (Decimal128) - Calculated tax (10% of subtotal)
- `shipping_amount` (Decimal128) - Shipping cost
- `discount_amount` (Decimal128) - Total discounts applied
- `total_amount` (Decimal128) - Final cart total
- `applied_coupons` (Array) - Coupon codes applied
- `created_at` (ISODate) - Cart creation timestamp
- `updated_at` (ISODate) - Last modification timestamp
- `expires_at` (ISODate) - Cart expiration (7 days from last update)

### Items Array Fields

Each item in the `items` array:
- `product_id` (String) - Product UUID
- `product_name` (String) - Product name snapshot
- `product_slug` (String) - URL-friendly name
- `product_sku` (String) - Stock keeping unit
- `quantity` (Int32) - Quantity in cart
- `unit_price` (Decimal128) - Price per unit
- `total_price` (Decimal128) - quantity * unit_price
- `image_url` (String) - Product image URL
- `is_available` (Boolean) - Product availability status
- `added_at` (ISODate) - When item was added

### Applied Coupons Array Fields

Each coupon in the `applied_coupons` array:
```json
{
  "coupon_code": "SAVE10",
  "discount_type": "PERCENTAGE",
  "discount_value": 10,
  "discount_amount": 449.99,
  "applied_at": ISODate("2024-10-27T11:50:00Z")
}
```

---

## Indexes

### Primary Index
- `_id` (Automatic, unique)

### Custom Indexes
```javascript
// Unique index on user_id (one cart per user)
db.carts.createIndex({ "user_id": 1 }, { unique: true })

// TTL index for auto-deletion of expired carts
db.carts.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 })

// Index on items.product_id for quick lookups
db.carts.createIndex({ "items.product_id": 1 })

// Compound index for queries
db.carts.createIndex({ "user_id": 1, "updated_at": -1 })
```

---

## TTL (Time To Live) Strategy

Carts automatically expire and get deleted after 7 days of inactivity:

1. **expires_at** is set to 7 days from creation
2. Every cart update resets **expires_at** to 7 days from now
3. MongoDB TTL index auto-deletes expired carts
4. Users can extend cart life by adding/removing items

---

## Validation Rules

MongoDB schema validation (optional but recommended):

```javascript
db.createCollection("carts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "items", "created_at", "updated_at", "expires_at"],
      properties: {
        user_id: {
          bsonType: "string",
          description: "User ID must be a string (UUID)"
        },
        items: {
          bsonType: "array",
          description: "Cart items array",
          items: {
            bsonType: "object",
            required: ["product_id", "quantity", "unit_price", "total_price"],
            properties: {
              product_id: { bsonType: "string" },
              quantity: { bsonType: "int", minimum: 1 },
              unit_price: { bsonType: "decimal" },
              total_price: { bsonType: "decimal" }
            }
          }
        },
        subtotal: { bsonType: "decimal" },
        total_amount: { bsonType: "decimal" },
        expires_at: { bsonType: "date" }
      }
    }
  }
})
```

---

## Redis Caching Strategy

Cart data is cached in Redis for ultra-fast access:

### Cache Key Pattern
```
cart:{user_id}
```

### Cache Flow
1. **GET /api/cart**
   - Check Redis first
   - If miss, fetch from MongoDB
   - Store in Redis with TTL of 1 hour

2. **POST /api/cart/items** (Add item)
   - Update MongoDB
   - Update Redis cache
   - Extend TTL

3. **DELETE /api/cart/items/:id** (Remove item)
   - Update MongoDB
   - Update Redis cache

4. **Cache Invalidation**
   - On checkout: Delete from Redis
   - On cart clear: Delete from Redis
   - On product price change: Invalidate related carts

---

## Business Logic

### Add Item to Cart
```python
1. Check if user has existing cart
2. If not, create new cart document
3. Check if product already in cart
   - If yes: Update quantity
   - If no: Add new item to items array
4. Recalculate subtotal, tax, total
5. Update updated_at and expires_at
6. Update Redis cache
```

### Remove Item from Cart
```python
1. Find cart by user_id
2. Remove item from items array
3. Recalculate totals
4. If items array empty, delete cart
5. Update Redis cache
```

### Update Item Quantity
```python
1. Find cart and item
2. Update item.quantity
3. Recalculate item.total_price
4. Recalculate cart totals
5. Update timestamps
6. Update Redis cache
```

### Calculate Cart Totals
```python
subtotal = sum(item.total_price for item in items)
tax_amount = subtotal * 0.10  # 10% tax
shipping_amount = 10.00 if subtotal < 500 else 0  # Free shipping over $500
discount_amount = sum(coupon.discount_amount for coupon in coupons)
total_amount = subtotal + tax_amount + shipping_amount - discount_amount
```

---

## Kafka Events

### Producer Events:
- `cart.item.added` - When item added to cart
- `cart.item.removed` - When item removed from cart
- `cart.item.updated` - When quantity updated
- `cart.cleared` - When cart is cleared after checkout

### Event Payload Example:
```json
{
  "event_type": "cart.item.added",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_id": "prod-123",
  "quantity": 1,
  "timestamp": "2024-10-27T12:00:00Z"
}
```

---

## APIs That Will Use This Schema

- GET `/api/cart` - Get user's cart
- POST `/api/cart/items` - Add item to cart
- PUT `/api/cart/items/:product_id` - Update item quantity
- DELETE `/api/cart/items/:product_id` - Remove item from cart
- DELETE `/api/cart` - Clear entire cart
- GET `/api/cart/total` - Get cart totals
- POST `/api/cart/coupon` - Apply coupon code
- DELETE `/api/cart/coupon/:code` - Remove coupon

---

## Django Integration

Using `djongo` or `pymongo`:

### Option 1: Djongo (Django ORM style)
```python
from djongo import models

class Cart(models.Model):
    user_id = models.CharField(max_length=36)
    items = models.JSONField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    # ... other fields
    
    class Meta:
        db_table = 'carts'
```

### Option 2: PyMongo (Recommended for flexibility)
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['cart_service_db']
carts_collection = db['carts']
```

---

## Sample Document

```json
{
  "_id": ObjectId("6540a1b2c3d4e5f6a7b8c9d0"),
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": [
    {
      "product_id": "prod-001",
      "product_name": "Wireless Mouse",
      "product_slug": "wireless-mouse",
      "product_sku": "MOUSE-WL-001",
      "quantity": 2,
      "unit_price": 29.99,
      "total_price": 59.98,
      "image_url": "https://cdn.example.com/mouse.jpg",
      "is_available": true,
      "added_at": ISODate("2024-10-27T10:00:00Z")
    }
  ],
  "subtotal": 59.98,
  "tax_amount": 5.99,
  "shipping_amount": 10.00,
  "discount_amount": 0.00,
  "total_amount": 75.97,
  "applied_coupons": [],
  "created_at": ISODate("2024-10-27T10:00:00Z"),
  "updated_at": ISODate("2024-10-27T10:00:00Z"),
  "expires_at": ISODate("2024-11-03T10:00:00Z")
}
```

---

## Performance Considerations

1. **Embedded Documents** - No joins needed, fast reads
2. **Redis Caching** - Sub-millisecond response times
3. **TTL Index** - Automatic cleanup of old carts
4. **Indexed Queries** - Fast lookups by user_id
5. **Atomic Operations** - MongoDB's findAndModify for consistency

---

## Migration from SQL (if needed)

If migrating from a relational cart system:

```python
# Old SQL schema
carts: id, user_id, created_at
cart_items: id, cart_id, product_id, quantity, price

# Convert to MongoDB document
{
  "user_id": cart.user_id,
  "items": [
    {item1}, {item2}, ...
  ],
  "created_at": cart.created_at
}
```
