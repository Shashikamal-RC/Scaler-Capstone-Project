# Complete System ER Diagram

## Complete E-Commerce System Entity-Relationship Diagram

This document provides the structure for creating a comprehensive ER diagram showing all services and their relationships.

---

## System Overview

The complete e-commerce system consists of **6 microservices** with **17 database entities**:

### Service Breakdown:
1. **User Service** - 5 PostgreSQL tables
2. **Product Service** - 5 PostgreSQL tables  
3. **Order Service** - 3 PostgreSQL tables
4. **Payment Service** - 3 PostgreSQL tables
5. **Cart Service** - 1 MongoDB collection
6. **Notification Service** - No database (event-driven)

**Total:** 16 PostgreSQL tables + 1 MongoDB collection

---

## Complete System Diagram Layout

### Recommended Layout (Landscape):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      E-COMMERCE MICROSERVICES ARCHITECTURE                    │
│                           Database Schema Overview                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                          USER SERVICE (PostgreSQL)                        │ │
│  ├──────────────────────────────────────────────────────────────────────────┤ │
│  │  ┌──────────┐   ┌────────────┐   ┌─────────────┐   ┌────────────────┐  │ │
│  │  │  users   │   │ user_roles │   │user_role_   │   │user_addresses  │  │ │
│  │  │  (5 FKs) │   │            │   │mapping      │   │                │  │ │
│  │  └────┬─────┘   └────┬───────┘   └─────────────┘   └────────────────┘  │ │
│  │       │              │                                                    │ │
│  │       │              │             ┌───────────────────────┐             │ │
│  │       └──────────────┘             │password_reset_tokens  │             │ │
│  │                                    └───────────────────────┘             │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                         │                                      │
│                                         │ user_id (Logical FK)                 │
│                         ┌───────────────┼───────────────┐                     │
│                         │               │               │                     │
│  ┌──────────────────────┼───────────────┼───────────────┼──────────────────┐ │
│  │  PRODUCT SERVICE (PostgreSQL)        │               │                   │ │
│  ├──────────────────────┼───────────────┼───────────────┼──────────────────┤ │
│  │  ┌────────────┐      │               │               │                   │ │
│  │  │categories  │      │               │               │                   │ │
│  │  │(self-ref)  │      │               │               │                   │ │
│  │  └─────┬──────┘      │               │               │                   │ │
│  │        │             │               │               │                   │ │
│  │        ▼             │               │               │                   │ │
│  │  ┌────────────┐      │               │               │                   │ │
│  │  │  products  │◄─────┤               │               │                   │ │
│  │  │  (Central) │      │  product_id   │               │                   │ │
│  │  └─────┬──────┘      │  (Logical FK) │               │                   │ │
│  │        │             │               │               │                   │ │
│  │    ┌───┴────┬────────┴─────┐         │               │                   │ │
│  │    ▼        ▼              ▼         │               │                   │ │
│  │  ┌────┐  ┌──────┐  ┌─────────────┐  │               │                   │ │
│  │  │images│ │inventory│ │product_   │  │               │                   │ │
│  │  │      │ │(1:1)   │ │reviews    │  │               │                   │ │
│  │  └──────┘ └────────┘ └─────────────┘  │               │                   │ │
│  └──────────────────────────────────────┼───────────────┼──────────────────┘ │
│                                          │               │                     │
│                                          │               │                     │
│  ┌──────────────────────────────────────┼───────────────┼──────────────────┐ │
│  │       CART SERVICE (MongoDB + Redis) │               │                   │ │
│  ├──────────────────────────────────────┼───────────────┼──────────────────┤ │
│  │                                      │               │                   │ │
│  │  Redis Cache: cart:{user_id}        │               │                   │ │
│  │  TTL: 1 hour                         │               │                   │ │
│  │         │                            │               │                   │ │
│  │         ▼                            │               │                   │ │
│  │  ┌────────────────────┐              │               │                   │ │
│  │  │  carts (MongoDB)   │◄─────────────┘               │                   │ │
│  │  │                    │                              │                   │ │
│  │  │  - user_id         │                              │                   │ │
│  │  │  - items: [        │──────────┐                   │                   │ │
│  │  │      {product_id}  │          │ product_id        │                   │ │
│  │  │    ]               │          │ (Logical FK)      │                   │ │
│  │  │  - totals          │          │                   │                   │ │
│  │  │  - expires_at      │          │                   │                   │ │
│  │  └────────────────────┘          │                   │                   │ │
│  └──────────────────────────────────┼───────────────────┼──────────────────┘ │
│                                     │                   │                     │
│                                     │                   │                     │
│  ┌─────────────────────────────────┼───────────────────┼──────────────────┐ │
│  │       ORDER SERVICE (PostgreSQL) │                   │                   │ │
│  ├──────────────────────────────────┼───────────────────┼──────────────────┤ │
│  │                                  │                   │                   │ │
│  │         ┌────────────────┐       │                   │                   │ │
│  │         │    orders      │◄──────┘                   │                   │ │
│  │         │                │                           │                   │ │
│  │         │ - user_id      │                           │                   │ │
│  │         │ - shipping_    │───────────────────────────┘ address_id        │ │
│  │         │   address_id   │                           (Logical FK)        │ │
│  │         │ - billing_     │───────────────────────────┐                   │ │
│  │         │   address_id   │                           │                   │ │
│  │         │ - status       │                           │                   │ │
│  │         │ - totals       │                           │                   │ │
│  │         └────┬───────────┘                           │                   │ │
│  │              │ 1                                     │                   │ │
│  │         ┌────┴────┐                                  │                   │ │
│  │         │ N       │ N                                │                   │ │
│  │         ▼         ▼                                  │                   │ │
│  │  ┌──────────┐ ┌─────────────────┐                  │                   │ │
│  │  │order_    │ │order_status_    │                  │                   │ │
│  │  │items     │ │history          │                  │                   │ │
│  │  │          │ │(Audit Trail)    │                  │                   │ │
│  │  │-product_id│─┘                │                  │                   │ │
│  │  └──────────┘  └─────────────────┘                  │                   │ │
│  └─────────────────────────────────────────────────────┼──────────────────┘ │
│                        │ order_id (Logical FK)          │                     │
│                        │                                │                     │
│  ┌─────────────────────┼────────────────────────────────┼──────────────────┐ │
│  │     PAYMENT SERVICE (PostgreSQL)                     │                   │ │
│  ├──────────────────────┼────────────────────────────────┼──────────────────┤ │
│  │                      │                                │                   │ │
│  │  ┌────────────────┐  │                                │                   │ │
│  │  │payment_methods │  │                                │                   │ │
│  │  │(Lookup)        │  │                                │                   │ │
│  │  └────┬───────────┘  │                                │                   │ │
│  │       │ 1            │                                │                   │ │
│  │   ┌───┴────┐         │                                │                   │ │
│  │   │ N      │ N       │                                │                   │ │
│  │   ▼        ▼         │                                │                   │ │
│  │ ┌────────┐ ┌──────────────────────┐                  │                   │ │
│  │ │trans-  │ │user_saved_payment_   │                  │                   │ │
│  │ │actions │ │methods               │                  │                   │ │
│  │ │        │ │                      │                  │                   │ │
│  │ │-order_ │◄┼──────────────────────┘                  │                   │ │
│  │ │ id     │ │                                          │                   │ │
│  │ │-user_id│◄┼──────────────────────────────────────────┘                   │ │
│  │ └────────┘ └──────────────────────┘                                       │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │     NOTIFICATION SERVICE (Event-Driven - No Database)                    │  │
│  ├──────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                           │  │
│  │  Listens to Kafka events:                                                │  │
│  │  • user.registered → Send welcome email                                  │  │
│  │  • order.created → Send order confirmation                               │  │
│  │  • order.shipped → Send shipping notification                            │  │
│  │  • payment.success → Send payment receipt                                │  │
│  │  • password.reset → Send reset email                                     │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Cross-Service Relationships Summary

### Logical Foreign Keys (Not Enforced by Database)

These relationships cross microservice boundaries and are enforced at the application level:

| From Service | From Table | Field | To Service | To Table | Cardinality |
|-------------|-----------|-------|------------|----------|-------------|
| Order | orders | user_id | User | users | N:1 |
| Order | orders | shipping_address_id | User | user_addresses | N:1 |
| Order | orders | billing_address_id | User | user_addresses | N:1 |
| Order | order_items | product_id | Product | products | N:1 |
| Payment | transactions | order_id | Order | orders | N:1 |
| Payment | transactions | user_id | User | users | N:1 |
| Payment | user_saved_payment_methods | user_id | User | users | N:1 |
| Cart | carts | user_id | User | users | 1:1 |
| Cart | carts.items | product_id | Product | products | N:1 |
| Product | product_reviews | user_id | User | users | N:1 |

---

## Service Dependencies Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                  Service Communication Flow                     │
│                                                                  │
│                    ┌─────────────┐                             │
│                    │ User Service│                             │
│                    │             │                             │
│                    │ • Auth      │                             │
│                    │ • Users     │                             │
│                    │ • Addresses │                             │
│                    └──────┬──────┘                             │
│                           │                                     │
│              ┌────────────┼────────────┐                       │
│              │            │            │                       │
│              ▼            ▼            ▼                       │
│      ┌───────────┐ ┌──────────┐ ┌──────────┐                 │
│      │  Product  │ │   Cart   │ │  Order   │                 │
│      │  Service  │ │  Service │ │ Service  │                 │
│      │           │ │          │ │          │                 │
│      │• Catalog  │ │• Shopping│ │• Orders  │                 │
│      │• Inventory│ │  Cart    │ │• Tracking│                 │
│      │• Reviews  │ │• Redis   │ │• Status  │                 │
│      └─────┬─────┘ └────┬─────┘ └────┬─────┘                 │
│            │            │            │                        │
│            │            └────────┐   └────────┐               │
│            │                     │            │               │
│            │                     ▼            ▼               │
│            │              ┌────────────┐ ┌────────────┐      │
│            │              │  Payment   │ │Notification│      │
│            │              │  Service   │ │  Service   │      │
│            │              │            │ │            │      │
│            │              │• Gateway   │ │• Email     │      │
│            │              │• Txn Log   │ │• Kafka     │      │
│            │              └────────────┘ └────────────┘      │
│            │                                                   │
│            └──────────────────────────────────────────────────┘
│                     (All services can fetch product data)      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Database Technology Breakdown

```
┌────────────────────────────────────────────────────────────────┐
│                    Database Distribution                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              PostgreSQL 16.x (RDBMS)                      │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │                                                           │ │
│  │  user_service_db:                                        │ │
│  │    • users                                               │ │
│  │    • user_roles                                          │ │
│  │    • user_role_mapping                                   │ │
│  │    • user_addresses                                      │ │
│  │    • password_reset_tokens                               │ │
│  │                                                           │ │
│  │  product_service_db:                                     │ │
│  │    • categories                                          │ │
│  │    • products                                            │ │
│  │    • product_images                                      │ │
│  │    • product_inventory                                   │ │
│  │    • product_reviews                                     │ │
│  │                                                           │ │
│  │  order_service_db:                                       │ │
│  │    • orders                                              │ │
│  │    • order_items                                         │ │
│  │    • order_status_history                                │ │
│  │                                                           │ │
│  │  payment_service_db:                                     │ │
│  │    • payment_methods                                     │ │
│  │    • transactions                                        │ │
│  │    • user_saved_payment_methods                          │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │               MongoDB 7.x (NoSQL)                         │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │                                                           │ │
│  │  cart_service_db:                                        │ │
│  │    • carts (collection)                                  │ │
│  │      - Flexible schema                                   │ │
│  │      - Embedded items array                              │ │
│  │      - TTL index (7 days)                                │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Redis 7.x (Cache)                            │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │                                                           │ │
│  │  • cart:{user_id} - Cart cache (TTL: 1 hour)            │ │
│  │  • session:{session_id} - User sessions                  │ │
│  │  • product:{product_id} - Product cache                  │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          Elasticsearch 8.x (Search Engine)                │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │                                                           │ │
│  │  • products_index - Product search                       │ │
│  │    - Full-text search                                    │ │
│  │    - Filters & facets                                    │ │
│  │    - Auto-suggest                                        │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Entity Count Summary

| Service | Database | Tables/Collections | Total Entities |
|---------|----------|-------------------|----------------|
| User Service | PostgreSQL | 5 tables | 5 |
| Product Service | PostgreSQL | 5 tables | 5 |
| Order Service | PostgreSQL | 3 tables | 3 |
| Payment Service | PostgreSQL | 3 tables | 3 |
| Cart Service | MongoDB | 1 collection | 1 |
| Notification Service | None | Event-driven | 0 |
| **TOTAL** | | | **17** |

---

## Relationship Summary

### Within-Service Relationships (17 total):

**User Service (5):**
1. users ↔ user_roles (M:N via user_role_mapping)
2. users → user_addresses (1:N)
3. users → password_reset_tokens (1:N)

**Product Service (5):**
4. categories → categories (1:N self-referencing)
5. categories → products (1:N)
6. products → product_images (1:N)
7. products ↔ product_inventory (1:1)
8. products → product_reviews (1:N)

**Order Service (2):**
9. orders → order_items (1:N)
10. orders → order_status_history (1:N)

**Payment Service (2):**
11. payment_methods → transactions (1:N)
12. payment_methods → user_saved_payment_methods (1:N)

**Cart Service (embedded):**
13. carts contains embedded items array

### Cross-Service Relationships (10 total - Logical):

14. orders.user_id → users.id
15. orders.shipping_address_id → user_addresses.id
16. orders.billing_address_id → user_addresses.id
17. order_items.product_id → products.id
18. transactions.order_id → orders.id
19. transactions.user_id → users.id
20. user_saved_payment_methods.user_id → users.id
21. carts.user_id → users.id
22. carts.items.product_id → products.id
23. product_reviews.user_id → users.id

---

## Kafka Event Flow

```
┌────────────────────────────────────────────────────────────────┐
│                      Kafka Topics & Events                      │
│                                                                  │
│  User Service Produces:                                         │
│    • user.registered                                            │
│    • user.updated                                               │
│    • user.deleted                                               │
│                                                                  │
│  Order Service Produces:                                        │
│    • order.created ──────► Payment Service, Notification       │
│    • order.confirmed ─────► Product Service (reserve inventory)│
│    • order.shipped ───────► Notification Service               │
│    • order.delivered ─────► Notification Service               │
│    • order.cancelled ─────► Product Service (release inventory)│
│                                                                  │
│  Payment Service Produces:                                      │
│    • payment.initiated                                          │
│    • payment.success ─────► Order Service, Notification        │
│    • payment.failed                                             │
│    • payment.refunded ────► Order Service, Notification        │
│                                                                  │
│  Product Service Produces:                                      │
│    • product.created                                            │
│    • product.updated                                            │
│    • product.out_of_stock                                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Draw.io Creation Steps

### 1. Create Service Boxes
- Use rounded rectangles for each service
- Different colors for each service
- Group entities within each service box

### 2. Add Entities
- Use rectangles for tables
- List key attributes
- Mark PK with 🔑
- Mark FK with 🔗

### 3. Draw Relationships
- Solid lines for within-service relationships
- Dashed/dotted lines for cross-service relationships
- Use crow's foot notation
- Label cardinality (1:1, 1:N, M:N)

### 4. Add Technology Labels
- PostgreSQL icon for SQL databases
- MongoDB icon for NoSQL
- Redis icon for cache
- Elasticsearch icon for search
- Kafka icon for message broker

### 5. Color Scheme
- User Service: Blue (#D6EAF8)
- Product Service: Green (#D5F4E6)
- Order Service: Orange (#FAE5D3)
- Payment Service: Purple (#E8DAEF)
- Cart Service: Red (#FADBD8)
- Notification Service: Yellow (#FEF9E7)

---

## Export Instructions

1. Create comprehensive system diagram (all services)
2. Create service dependencies diagram
3. Create database distribution diagram
4. Create Kafka event flow diagram
5. Export all as:
   - PNG (300 DPI, A3 landscape for report)
   - SVG (scalable for documentation)
   - PDF (for presentations)

Recommended dimensions: 2560x1440 (for comprehensive view)

---

## Figure Captions for Report

**Figure X.10: Complete E-Commerce System ER Diagram**

*This comprehensive diagram illustrates the complete microservices architecture with 6 services and 17 database entities. The system uses a polyglot persistence strategy with PostgreSQL for relational data (16 tables across 4 services), MongoDB for flexible cart storage, Redis for caching, Elasticsearch for product search, and Kafka for asynchronous inter-service communication. Solid lines represent within-service relationships enforced by database constraints, while dashed lines represent cross-service logical relationships enforced at the application level.*

**Figure X.11: Service Dependencies Diagram**

*This diagram shows the communication flow between microservices. The User Service provides centralized authentication, with dependent services (Product, Cart, Order, Payment) referencing user data. The Cart Service bridges the Product and Order services, facilitating the shopping-to-purchase flow. The Payment Service integrates with Order Service for transaction processing. The Notification Service consumes events from all services via Kafka to send customer communications.*

**Figure X.12: Database Technology Distribution**

*The system implements a polyglot persistence architecture with four database technologies. PostgreSQL hosts 16 tables across 4 separate databases (user_service_db, product_service_db, order_service_db, payment_service_db) for transactional data with ACID guarantees. MongoDB provides flexible schema storage for the cart service with TTL-based expiration. Redis caches frequently accessed data with sub-millisecond latency. Elasticsearch indexes product data for full-text search with filters and auto-suggest capabilities.*
