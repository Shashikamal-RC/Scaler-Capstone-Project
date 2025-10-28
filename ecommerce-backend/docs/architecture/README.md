# ER Diagrams - Overview

## Entity-Relationship Diagrams for E-Commerce Microservices

This directory contains comprehensive ER diagram documentation for all microservices in the e-commerce platform.

---

## 📋 Table of Contents

1. [Individual Service Diagrams](#individual-service-diagrams)
2. [Complete System Diagram](#complete-system-diagram)
3. [How to Use These Documents](#how-to-use-these-documents)
4. [Creating Diagrams in Draw.io](#creating-diagrams-in-drawio)
5. [Export Guidelines](#export-guidelines)

---

## 📊 Individual Service Diagrams

### 1. User Service ER Diagram
**File:** [er-diagram-user-service.md](./er-diagram-user-service.md)

**Entities:** 5 tables
- users (main entity)
- user_roles (lookup)
- user_role_mapping (junction)
- user_addresses
- password_reset_tokens

**Key Relationships:**
- users ↔ user_roles (M:N)
- users → user_addresses (1:N)
- users → password_reset_tokens (1:N)

---

### 2. Product Service ER Diagram
**File:** [er-diagram-product-service.md](./er-diagram-product-service.md)

**Entities:** 5 tables
- categories (hierarchical, self-referencing)
- products (main entity)
- product_images
- product_inventory (1:1 with products)
- product_reviews

**Key Relationships:**
- categories → categories (1:N self-referencing)
- categories → products (1:N)
- products → product_images (1:N)
- products ↔ product_inventory (1:1)
- products → product_reviews (1:N)

**Special Features:**
- Elasticsearch integration for search
- JSONB for product dimensions
- Category hierarchy support

---

### 3. Order Service ER Diagram
**File:** [er-diagram-order-service.md](./er-diagram-order-service.md)

**Entities:** 3 tables
- orders (main entity)
- order_items (line items with product snapshots)
- order_status_history (audit trail)

**Key Relationships:**
- orders → order_items (1:N)
- orders → order_status_history (1:N)

**Special Features:**
- Order status flow diagram
- Product snapshot for price history
- Complete audit trail
- Cross-service references to User and Product services

---

### 4. Payment Service ER Diagram
**File:** [er-diagram-payment-service.md](./er-diagram-payment-service.md)

**Entities:** 3 tables
- payment_methods (lookup)
- transactions (main entity)
- user_saved_payment_methods (tokenized payment info)

**Key Relationships:**
- payment_methods → transactions (1:N)
- payment_methods → user_saved_payment_methods (1:N)

**Special Features:**
- Payment gateway integration (Razorpay, Stripe)
- PCI-DSS compliance notes
- Transaction state diagram
- JSONB for gateway responses
- Encrypted token storage

---

### 5. Cart Service ER Diagram
**File:** [er-diagram-cart-service.md](./er-diagram-cart-service.md)

**Database:** MongoDB (NoSQL)

**Collection:** 1 document collection
- carts (with embedded items array)

**Special Features:**
- Document-based structure (not relational)
- Redis caching layer (1-hour TTL)
- MongoDB TTL index (7-day expiration)
- Cart operations flow diagram
- Cache strategy diagram

**Key Characteristics:**
- One cart per user (user_id unique)
- Embedded items with product snapshots
- Two-tier caching (Redis + MongoDB)
- Automatic expiration for abandoned carts

---

### 6. Notification Service
**Note:** Notification Service is event-driven and has **no database**.

It consumes Kafka events:
- user.registered
- order.created
- order.shipped
- payment.success
- password.reset

---

## 🌐 Complete System Diagram

**File:** [er-diagram-complete-system.md](./er-diagram-complete-system.md)

This diagram shows:
- All 6 microservices
- All 17 database entities
- Within-service relationships (solid lines)
- Cross-service logical relationships (dashed lines)
- Database technology distribution
- Service dependencies
- Kafka event flow

**Statistics:**
- **Total Entities:** 17 (16 PostgreSQL tables + 1 MongoDB collection)
- **Within-Service Relationships:** 13
- **Cross-Service Relationships:** 10 (logical FKs)
- **PostgreSQL Databases:** 4 (one per service)
- **MongoDB Databases:** 1 (Cart Service)
- **Cache Layers:** Redis
- **Search Engine:** Elasticsearch
- **Message Broker:** Apache Kafka

---

## 📖 How to Use These Documents

### For Development
1. **Reference during coding:** Use entity attributes when creating Django models
2. **API design:** Understand relationships when designing endpoints
3. **Database migrations:** Follow the schema definitions for creating tables
4. **Query optimization:** Use index information for performance tuning

### For Academic Report
1. **Copy entity definitions** directly into your report
2. **Use figure captions** provided in each document
3. **Include visual diagrams** created from the specifications
4. **Reference cardinality** and relationship explanations

### For Draw.io Creation
Each document includes:
- ✅ Entity layout suggestions
- ✅ Attribute lists with icons
- ✅ Relationship notation (crow's foot)
- ✅ Color coding recommendations
- ✅ Flow diagrams (where applicable)
- ✅ Export instructions

---

## 🎨 Creating Diagrams in Draw.io

### Step-by-Step Process:

#### 1. Open Draw.io
- Visit: https://app.diagrams.net/
- Or use VS Code extension: `Draw.io Integration`

#### 2. Create New Diagram
- File → New → Blank Diagram
- Choose: A4 Landscape (for individual services)
- Choose: A3 Landscape (for complete system)

#### 3. Add Entities
**Entity Rectangle:**
```
┌─────────────────┐
│   table_name    │ ← Header (colored background)
├─────────────────┤
│ 🔑 id (PK)      │ ← Primary key
│ 📝 name         │ ← Regular attribute
│ 🔗 fk_id (FK)   │ ← Foreign key
│ 📅 created_at   │ ← Timestamp
└─────────────────┘
```

**Steps:**
1. Insert → Rectangle
2. Double-click to add text
3. Format → Fill color (choose from color scheme)
4. Format → Stroke → 2pt border

#### 4. Add Relationships
**Crow's Foot Notation:**
- Insert → Line → Connector
- Click start entity, then end entity
- Right-click line → Edit Style → Choose arrow type

**Arrow Types:**
- One (1): `|` (single line)
- Many (N): `<` (crow's foot)
- One-to-One: `|────|`
- One-to-Many: `|────<`
- Many-to-Many: `<────<` (via junction table)

**For cross-service (logical FKs):**
- Use dashed/dotted line style
- Format → Dashed → Yes

#### 5. Add Labels
- Double-click relationship line
- Add cardinality: "1", "N", "1:1", "1:N", "M:N"
- Add FK field name if needed

#### 6. Color Scheme

Use these colors for consistency:

| Service | Color Name | Hex Code |
|---------|-----------|----------|
| User Service | Light Blue | #D6EAF8 |
| Product Service | Light Green | #D5F4E6 |
| Order Service | Light Orange | #FAE5D3 |
| Payment Service | Light Purple | #E8DAEF |
| Cart Service | Light Red | #FADBD8 |
| Notification Service | Light Yellow | #FEF9E7 |
| Lookup Tables | Light Yellow | #FEF9E7 |
| Junction Tables | Light Green | #D5F4E6 |

#### 7. Icons for Attributes

Copy-paste these emoji icons:

| Icon | Meaning |
|------|---------|
| 🔑 | Primary Key |
| 🔗 | Foreign Key |
| 📝 | Text/String |
| 💰 | Money/Decimal |
| 📅 | Date/Timestamp |
| ✓ | Boolean |
| 📊 | Enum/Status |
| 🔢 | Integer/Number |
| 📱 | Phone |
| ✉️ | Email |
| 🔒 | Password |
| 🏠 | Address |
| 🖼️ | Image URL |
| 📦 | SKU/Product |
| ⭐ | Rating |
| 💳 | Payment |

---

## 📤 Export Guidelines

### For Academic Report (Print)

**Format:** PNG or PDF
**Resolution:** 300 DPI
**Size:** A4 or A3 landscape
**Color:** Full color

**Steps:**
1. File → Export as → PNG (or PDF)
2. Select: Transparent background = No
3. Select: Resolution = 300 DPI
4. Select: Border width = 10px
5. Click Export

**File naming:**
```
figure-1-user-service-er-diagram.png
figure-2-product-service-er-diagram.png
figure-3-order-service-er-diagram.png
...
```

### For Web Documentation

**Format:** SVG
**Reason:** Scalable, crisp at any zoom level

**Steps:**
1. File → Export as → SVG
2. Select: Embed fonts = Yes
3. Select: Include copy of diagram = Yes (allows future editing)
4. Click Export

### For Presentations

**Format:** PDF
**Size:** 16:9 or 4:3 aspect ratio

**Steps:**
1. File → Page Setup → Change to presentation size
2. File → Export as → PDF
3. Select: All pages
4. Click Export

---

## 📁 Recommended File Structure

After creating diagrams, organize them:

```
ecommerce-backend/docs/architecture/
├── README.md (this file)
├── er-diagram-user-service.md
├── er-diagram-product-service.md
├── er-diagram-order-service.md
├── er-diagram-payment-service.md
├── er-diagram-cart-service.md
├── er-diagram-complete-system.md
└── diagrams/
    ├── draw-io-source/
    │   ├── user-service.drawio
    │   ├── product-service.drawio
    │   ├── order-service.drawio
    │   ├── payment-service.drawio
    │   ├── cart-service.drawio
    │   └── complete-system.drawio
    ├── png/
    │   ├── user-service-er.png
    │   ├── product-service-er.png
    │   ├── order-service-er.png
    │   ├── payment-service-er.png
    │   ├── cart-service-er.png
    │   └── complete-system-er.png
    ├── svg/
    │   └── (SVG versions for web)
    └── pdf/
        └── (PDF versions for presentation)
```

---

## 🔍 Quick Reference

### Database Technologies Used

| Technology | Version | Purpose | Services Using It |
|-----------|---------|---------|-------------------|
| PostgreSQL | 16.x | Relational data | User, Product, Order, Payment |
| MongoDB | 7.x | Document store | Cart |
| Redis | 7.x | Cache layer | Cart (+ future session storage) |
| Elasticsearch | 8.x | Search engine | Product |
| Apache Kafka | 3.x | Message broker | All services |

### Total Entity Count

| Database | Entity Type | Count |
|----------|------------|-------|
| PostgreSQL | Tables | 16 |
| MongoDB | Collections | 1 |
| **Total** | **Entities** | **17** |

### Relationship Count

| Type | Count | Description |
|------|-------|-------------|
| Within-Service | 13 | Enforced by database FK constraints |
| Cross-Service | 10 | Logical references, app-level enforcement |
| **Total** | **23** | **All relationships** |

---

## ✅ Checklist for ER Diagram Creation

- [ ] Read all 6 service-specific ER diagram documents
- [ ] Read complete system ER diagram document
- [ ] Open Draw.io (web or VS Code extension)
- [ ] Create User Service diagram
- [ ] Create Product Service diagram
- [ ] Create Order Service diagram
- [ ] Create Payment Service diagram
- [ ] Create Cart Service diagram (MongoDB structure)
- [ ] Create Complete System diagram
- [ ] Create Service Dependencies diagram
- [ ] Create Database Distribution diagram
- [ ] Create Kafka Event Flow diagram
- [ ] Export all diagrams as PNG (300 DPI)
- [ ] Export all diagrams as SVG
- [ ] Export all diagrams as PDF
- [ ] Add diagrams to academic report with captions
- [ ] Commit diagrams to Git repository

---

## 📚 Additional Resources

### Draw.io Tutorials
- Official Guide: https://www.drawio.com/doc/
- ER Diagram Tutorial: https://drawio-app.com/entity-relationship-diagrams-with-draw-io/
- Crow's Foot Notation: https://vertabelo.com/blog/crow-s-foot-notation/

### Database Design Best Practices
- PostgreSQL Documentation: https://www.postgresql.org/docs/16/
- MongoDB Schema Design: https://www.mongodb.com/docs/manual/core/data-modeling-introduction/
- Microservices Data Patterns: https://microservices.io/patterns/data/database-per-service.html

---

## 🤝 Contributing

When updating diagrams:
1. Update the corresponding `.md` file first
2. Recreate the diagram in Draw.io
3. Export in all formats (PNG, SVG, PDF)
4. Update this README if adding new diagrams
5. Commit with clear message: `Update [service] ER diagram - [reason]`

---

## 📄 License

These diagrams are part of the Scaler Neovarsity Capstone Project.

**Student:** Shashikamal RC  
**Guide:** Naman Bhalla  
**Institution:** Scaler Neovarsity - Woolf  
**Year:** 2025

---

## 📞 Support

For questions or clarifications:
- Review individual diagram documentation
- Check database schema files in `docs/database/`
- Refer to PRD and HLD documents in project root

---

**Last Updated:** October 28, 2025  
**Version:** 1.0  
**Status:** Documentation Complete - Ready for Diagram Creation
