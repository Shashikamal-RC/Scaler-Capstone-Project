# Database Schema Documentation

## 📚 Documentation Structure

### By Microservice (Detailed Schemas)

1. **[User Service Schema](./user-service-schema.md)**
   - 5 tables: users, user_roles, user_role_mapping, user_addresses, password_reset_tokens
   - Authentication, roles, addresses management

2. **[Product Service Schema](./product-service-schema.md)**
   - 5 tables: categories, products, product_images, product_inventory, product_reviews
   - Product catalog, inventory, reviews

3. **[Order Service Schema](./order-service-schema.md)**
   - 3 tables: orders, order_items, order_status_history
   - Order processing and tracking

4. **[Payment Service Schema](./payment-service-schema.md)**
   - 3 tables: payment_methods, transactions, user_saved_payment_methods
   - Payment processing and transactions

5. **[Cart Service Schema](./cart-service-schema.md)**
   - 1 collection: carts (MongoDB)
   - Shopping cart with Redis caching

### Common Documentation

6. **[Design Principles](./design-principles.md)**
   - Naming conventions
   - Data type standards
   - Index strategy
   - Normalization guidelines
   - Security best practices
   - Performance optimization

7. **[Schema Summary](./schema-summary.md)**
   - Quick reference for all tables
   - Foreign keys and relationships
   - Cardinality definitions
   - Formatted for academic report

8. **[Complete Schema](./schema.md)**
   - All schemas in one document
   - Legacy reference

---

## Quick Overview

### Total Entities: 17

**PostgreSQL (16 tables):**
- User Service: 5 tables
- Product Service: 5 tables
- Order Service: 3 tables
- Payment Service: 3 tables

**MongoDB (1 collection):**
- Cart Service: 1 collection

---

## Database Distribution

```
┌─────────────────────┐
│   User Service DB   │
│   (PostgreSQL)      │
│                     │
│ • users             │
│ • user_roles        │
│ • user_role_mapping │
│ • user_addresses    │
│ • password_tokens   │
└─────────────────────┘

┌─────────────────────┐
│  Product Service DB │
│   (PostgreSQL)      │
│                     │
│ • categories        │
│ • products          │
│ • product_images    │
│ • product_inventory │
│ • product_reviews   │
└─────────────────────┘

┌─────────────────────┐
│   Order Service DB  │
│   (PostgreSQL)      │
│                     │
│ • orders            │
│ • order_items       │
│ • order_status_     │
│   history           │
└─────────────────────┘

┌─────────────────────┐
│  Payment Service DB │
│   (PostgreSQL)      │
│                     │
│ • payment_methods   │
│ • transactions      │
│ • user_saved_       │
│   payment_methods   │
└─────────────────────┘

┌─────────────────────┐
│   Cart Service DB   │
│   (MongoDB)         │
│                     │
│ • carts             │
│   (collection)      │
└─────────────────────┘
```

---

## Key Design Decisions

### Why PostgreSQL?
- ACID compliance for transactions
- Strong relational integrity
- Excellent JSON support (JSONB)
- Mature ecosystem

### Why MongoDB for Carts?
- Flexible schema for cart items
- Fast read/write performance
- TTL indexes for auto-expiration
- Easy integration with Redis

### Why Database Per Service?
- Independent scaling
- Technology flexibility
- Fault isolation
- Clear ownership

---

## ER Diagrams

ER diagrams will be created using draw.io:
- [ ] User Service ER Diagram
- [ ] Product Service ER Diagram
- [ ] Order Service ER Diagram
- [ ] Payment Service ER Diagram
- [ ] Cart Service Schema Diagram
- [ ] Complete System ER Diagram

---

## Next Steps

1. ✅ Schema design completed and documented
2. ⏳ Create ER diagrams using draw.io
3. ⏳ Implement Django models
4. ⏳ Create database migrations
5. ⏳ Seed initial data

---

## Navigation Guide

**For Development:**
- Start with [Design Principles](./design-principles.md)
- Then read individual service schemas

**For Report:**
- Use [Schema Summary](./schema-summary.md)
- Reference [Design Principles](./design-principles.md)

**For Quick Reference:**
- See table of contents above
- Each service schema is self-contained
