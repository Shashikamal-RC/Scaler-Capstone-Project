# User Service Database Schema

## Database: user_service_db (PostgreSQL)

This database handles all user-related data including authentication, roles, and addresses.

---

## Tables

### 1. users
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

**Django Model Considerations:**
- Use `AbstractBaseUser` for built-in password hashing
- Use `UUIDField` for primary key
- Use `EmailField` with validators

---

### 2. user_roles
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

### 3. user_role_mapping
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

**Django Model Considerations:**
- Use `ManyToManyField` with through table
- Custom through model for `assigned_at` timestamp

---

### 4. user_addresses
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

**Django Model Considerations:**
- Use `TextChoices` for address_type enum
- ForeignKey with `related_name='addresses'`

---

### 5. password_reset_tokens
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

**Django Model Considerations:**
- Auto-generate token using `secrets.token_urlsafe()`
- Set expiration to 1 hour from creation
- Cleanup expired tokens with periodic task

---

## Relationships

### users ↔ user_roles (Many-to-Many via user_role_mapping)
- One user can have multiple roles
- One role can belong to multiple users
- **Cardinality: M:N**

### users → user_addresses (One-to-Many)
- One user can have multiple addresses
- One address belongs to one user
- **Cardinality: 1:N**

### users → password_reset_tokens (One-to-Many)
- One user can have multiple reset tokens
- One token belongs to one user
- **Cardinality: 1:N**

---

## Foreign Keys Summary

- `user_role_mapping(user_id)` REFERENCES `users(id)` ON DELETE CASCADE
- `user_role_mapping(role_id)` REFERENCES `user_roles(id)` ON DELETE CASCADE
- `user_addresses(user_id)` REFERENCES `users(id)` ON DELETE CASCADE
- `password_reset_tokens(user_id)` REFERENCES `users(id)` ON DELETE CASCADE

---

## Cross-Service References (Logical)

The `users.id` is referenced by other services:
- Order Service: `orders.user_id`
- Payment Service: `transactions.user_id`
- Product Service: `product_reviews.user_id`
- Cart Service: `carts.user_id`

These are **logical references** only (not enforced by foreign keys due to microservices architecture).

---

## APIs That Will Use This Schema

- POST `/api/users/register` - Create user
- POST `/api/users/login` - Authenticate user
- GET `/api/users/profile` - Get user profile
- PUT `/api/users/profile` - Update user profile
- POST `/api/users/reset-password` - Request password reset
- GET `/api/users/addresses` - Get user addresses
- POST `/api/users/addresses` - Add new address

---

## Sample Data

### users
```sql
INSERT INTO users (id, email, password, first_name, last_name, is_active, is_verified)
VALUES 
  ('550e8400-e29b-41d4-a716-446655440000', 'admin@example.com', 'hashed_password', 'Admin', 'User', TRUE, TRUE),
  ('550e8400-e29b-41d4-a716-446655440001', 'customer@example.com', 'hashed_password', 'John', 'Doe', TRUE, TRUE);
```

### user_roles
```sql
INSERT INTO user_roles (name, description)
VALUES 
  ('CUSTOMER', 'Regular customer'),
  ('ADMIN', 'Administrator with full access'),
  ('MANAGER', 'Store manager');
```
