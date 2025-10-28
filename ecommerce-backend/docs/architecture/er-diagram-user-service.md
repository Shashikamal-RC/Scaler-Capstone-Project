# User Service ER Diagram

## Entity Relationship Diagram - User Service

This document provides the structure for creating the ER diagram in draw.io.

---

## Entities and Attributes

### 1. users (Main Entity)
**Attributes:**
- 🔑 id (PK) - UUID
- ✉️ email (UNIQUE) - VARCHAR(255)
- 🔒 password - VARCHAR(255)
- 👤 first_name - VARCHAR(100)
- 👤 last_name - VARCHAR(100)
- 📱 phone_number (UNIQUE) - VARCHAR(20)
- ✓ is_active - BOOLEAN
- ✓ is_verified - BOOLEAN
- 📅 created_at - TIMESTAMP
- 📅 updated_at - TIMESTAMP

### 2. user_roles (Lookup Entity)
**Attributes:**
- 🔑 id (PK) - SERIAL
- 📝 name (UNIQUE) - VARCHAR(50)
- 📝 description - TEXT
- 📅 created_at - TIMESTAMP

### 3. user_role_mapping (Junction Table)
**Attributes:**
- 🔑 id (PK) - SERIAL
- 🔗 user_id (FK) - UUID → users.id
- 🔗 role_id (FK) - INTEGER → user_roles.id
- 📅 assigned_at - TIMESTAMP

### 4. user_addresses
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 user_id (FK) - UUID → users.id
- 📝 address_type - ENUM('SHIPPING', 'BILLING')
- 👤 full_name - VARCHAR(200)
- 📱 phone_number - VARCHAR(20)
- 🏠 address_line1 - VARCHAR(255)
- 🏠 address_line2 - VARCHAR(255)
- 🏙️ city - VARCHAR(100)
- 🏙️ state - VARCHAR(100)
- 📮 postal_code - VARCHAR(20)
- 🌍 country - VARCHAR(100)
- ✓ is_default - BOOLEAN
- 📅 created_at - TIMESTAMP
- 📅 updated_at - TIMESTAMP

### 5. password_reset_tokens
**Attributes:**
- 🔑 id (PK) - UUID
- 🔗 user_id (FK) - UUID → users.id
- 🔐 token (UNIQUE) - VARCHAR(255)
- ⏰ expires_at - TIMESTAMP
- ✓ is_used - BOOLEAN
- 📅 created_at - TIMESTAMP

---

## Relationships

### 1. users ↔ user_roles (Many-to-Many)
```
users ----------< user_role_mapping >---------- user_roles
  1                      N              N            1
```
- **Cardinality:** M:N
- **Relationship:** One user can have multiple roles; one role can belong to multiple users
- **Implementation:** Through junction table `user_role_mapping`

### 2. users → user_addresses (One-to-Many)
```
users ----------< user_addresses
  1                      N
```
- **Cardinality:** 1:N
- **Relationship:** One user can have multiple addresses
- **Foreign Key:** user_addresses.user_id → users.id
- **ON DELETE:** CASCADE

### 3. users → password_reset_tokens (One-to-Many)
```
users ----------< password_reset_tokens
  1                      N
```
- **Cardinality:** 1:N
- **Relationship:** One user can have multiple reset tokens
- **Foreign Key:** password_reset_tokens.user_id → users.id
- **ON DELETE:** CASCADE

---

## Draw.io Instructions

### Layout Suggestion:
```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│        ┌─────────────┐              ┌──────────────┐        │
│        │ user_roles  │              │    users     │        │
│        │             │              │  (Central)   │        │
│        │ - id (PK)   │              │              │        │
│        │ - name      │              │ - id (PK)    │        │
│        │ - description│             │ - email      │        │
│        └──────┬──────┘              │ - password   │        │
│               │                      │ - first_name │        │
│               │ N                    │ - last_name  │        │
│               │                      │ - phone      │        │
│               │                      │ - is_active  │        │
│        ┌──────┴────────────┐        │ - is_verified│        │
│        │ user_role_mapping │        └──────┬───────┘        │
│        │                   │               │                 │
│        │ - id (PK)         │               │ 1               │
│        │ - user_id (FK)────┼───────────────┤                 │
│        │ - role_id (FK)    │               │                 │
│        │ - assigned_at     │               │                 │
│        └───────────────────┘               │                 │
│                                            │                 │
│                                 ┌──────────┴──────────┐     │
│                                 │                      │     │
│                                 │ 1                   1│     │
│                                 │                      │     │
│                    ┌────────────┴──────┐   ┌─────────┴─────────┐
│                    │ user_addresses    │   │ password_reset_   │
│                    │                   │   │ tokens            │
│                    │ - id (PK)         │   │                   │
│                    │ - user_id (FK)    │   │ - id (PK)         │
│                    │ - address_type    │   │ - user_id (FK)    │
│                    │ - full_name       │   │ - token           │
│                    │ - phone_number    │   │ - expires_at      │
│                    │ - address_line1   │   │ - is_used         │
│                    │ - address_line2   │   │ - created_at      │
│                    │ - city            │   │                   │
│                    │ - state           │   └───────────────────┘
│                    │ - postal_code     │                        │
│                    │ - country         │                        │
│                    │ - is_default      │                        │
│                    │ - created_at      │                        │
│                    │ - updated_at      │                        │
│                    └───────────────────┘                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Steps to Create in Draw.io:

1. **Create Entities (Tables)**
   - Use rectangle shape for each table
   - Add table name in header
   - List all attributes below
   - Mark PK with key icon 🔑
   - Mark FK with link icon 🔗

2. **Add Relationships**
   - Use crow's foot notation
   - One side: Single line (1)
   - Many side: Crow's foot (N or ∞)
   - Label relationship lines

3. **Styling**
   - Primary keys: Bold text
   - Foreign keys: Italic text
   - Table headers: Different background color
   - Relationship lines: Arrows with labels

4. **Color Coding**
   - users (Main entity): Light blue
   - user_roles (Lookup): Light yellow
   - user_role_mapping (Junction): Light green
   - user_addresses: Light purple
   - password_reset_tokens: Light orange

---

## Crow's Foot Notation Guide

```
One (1):     ──────|
             
Many (N):    ──────<
             
Zero or One: ──────o|
             
Zero or Many:──────o<
```

### Relationship Examples:

**One-to-Many (1:N):**
```
users ──────|──────< user_addresses
(parent)  1     N    (child)
```

**Many-to-Many (M:N):**
```
users ──────|──────< user_role_mapping >──────|────── user_roles
        1          N                   N          1
```

---

## Cross-Service Relationships (Logical References)

These should be shown with dotted lines in the complete system diagram:

```
users.id ┈┈┈┈> orders.user_id (Order Service)
users.id ┈┈┈┈> transactions.user_id (Payment Service)
users.id ┈┈┈┈> product_reviews.user_id (Product Service)
users.id ┈┈┈┈> carts.user_id (Cart Service)

user_addresses.id ┈┈┈┈> orders.shipping_address_id (Order Service)
user_addresses.id ┈┈┈┈> orders.billing_address_id (Order Service)
```

Note: Use dotted/dashed lines for cross-service references as they are logical, not enforced by database FK.

---

## Sample Data Flow Diagram

```
Registration Flow:
1. Create user in 'users' table
2. Assign default role (CUSTOMER) in 'user_role_mapping'
3. User adds address in 'user_addresses'
4. Email verification via 'password_reset_tokens' (similar flow)

Password Reset Flow:
1. User requests reset
2. Generate token in 'password_reset_tokens'
3. Send email with token
4. User clicks link, validates token
5. Update password in 'users'
6. Mark token as used
```

---

## Export Instructions

Once created in draw.io:
1. File → Export as → PNG (for report)
2. File → Export as → SVG (for documentation)
3. File → Export as → PDF (for presentation)

Recommended size: 1920x1080 or A4 landscape

---

## Figure Caption for Report

**Figure X.1: User Service Entity-Relationship Diagram**

*This diagram illustrates the database schema for the User Service, showing five entities: users (main entity), user_roles (lookup table), user_role_mapping (junction table for many-to-many relationship), user_addresses, and password_reset_tokens. The diagram demonstrates one-to-many relationships between users and addresses/tokens, and a many-to-many relationship between users and roles implemented through the junction table.*
