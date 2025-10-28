# Common Database Design Principles

This document outlines the common design principles, standards, and conventions used across all microservice databases.

---

## Data Type Standards

### Primary Keys
- **UUID (PostgreSQL)**: For distributed systems compatibility
- **ObjectId (MongoDB)**: Default MongoDB identifier
- **SERIAL**: Only for lookup tables (roles, payment_methods)

### Money Fields
- **DECIMAL(10,2)**: For all currency values
- Never use FLOAT or DOUBLE for money (precision issues)
- Always store in smallest currency unit internally (optional)

### Text Fields
- **VARCHAR(n)**: For fixed-length or limited text
- **TEXT**: For unlimited length text
- **JSONB (PostgreSQL)**: For structured JSON data (indexable)

### Date/Time Fields
- **TIMESTAMP**: For all datetime values
- Always store in UTC
- Use `DEFAULT NOW()` for created_at
- Use triggers or Django for auto-updating updated_at

### Boolean Fields
- **BOOLEAN**: For true/false values
- Use `DEFAULT FALSE` or `DEFAULT TRUE` as appropriate
- Prefix with `is_`, `has_`, `can_` for clarity

---

## Naming Conventions

### Tables
- Lowercase with underscores: `user_addresses`, `order_items`
- Plural names: `users`, `products`, `orders`
- Junction tables: `table1_table2` (e.g., `user_role_mapping`)

### Columns
- Lowercase with underscores: `first_name`, `created_at`
- Foreign keys: `table_name_id` (e.g., `user_id`, `product_id`)
- Booleans: `is_active`, `has_discount`, `can_backorder`
- Timestamps: `created_at`, `updated_at`, `deleted_at`

### Indexes
- `idx_tablename_columnname` (e.g., `idx_users_email`)
- `uk_tablename_columnname` for unique (e.g., `uk_users_email`)
- Foreign keys auto-indexed by Django

### Constraints
- `fk_table1_table2` for foreign keys
- `chk_tablename_condition` for check constraints
- `uk_tablename_columns` for unique constraints

---

## Index Strategy

### Always Index
1. **Primary keys** - Automatic
2. **Foreign keys** - For join performance
3. **Unique constraints** - email, sku, order_number
4. **Frequently queried fields** - status, is_active, created_at

### Consider Indexing
1. **WHERE clause fields** - Columns used in filters
2. **ORDER BY fields** - Sorting columns
3. **GROUP BY fields** - Aggregation columns

### Don't Over-Index
- Write performance impact
- Storage overhead
- Maintenance cost

---

## Foreign Key Guidelines

### ON DELETE Actions

**CASCADE** - When parent deleted, delete children
- Use for: order_items, product_images, user_addresses
- Example: Delete user → Delete their addresses

**RESTRICT** - Prevent delete if children exist
- Use for: categories (if products exist), payment_methods
- Example: Can't delete category if products use it

**SET NULL** - Set foreign key to NULL when parent deleted
- Use for: parent_id in categories (hierarchy)
- Example: Delete parent category → Child category's parent_id = NULL

**SET DEFAULT** - Set to default value
- Rarely used in our design

---

## Cardinality Patterns

### One-to-One (1:1)
```
products ↔ product_inventory
```
- Use `OneToOneField` in Django
- UNIQUE constraint on foreign key

### One-to-Many (1:N)
```
users → user_addresses
categories → products
orders → order_items
```
- Use `ForeignKey` in Django
- Most common relationship

### Many-to-Many (M:N)
```
users ↔ user_roles (via user_role_mapping)
```
- Use `ManyToManyField` in Django
- Requires junction/through table
- Add timestamps in through table

---

## Normalization Guidelines

### 1NF (First Normal Form)
- ✅ All columns contain atomic values
- ✅ Each column contains single value type
- ✅ Each column has unique name
- ✅ Order doesn't matter

### 2NF (Second Normal Form)
- ✅ Meets 1NF
- ✅ All non-key attributes depend on entire primary key
- ✅ No partial dependencies

### 3NF (Third Normal Form)
- ✅ Meets 2NF
- ✅ No transitive dependencies
- ✅ Non-key attributes depend only on primary key

### Acceptable Denormalization
- **order_items**: Store product_name, product_sku (historical snapshot)
- **carts**: Embed product details (performance, no joins)
- **Reason**: Data integrity for historical records, performance optimization

---

## Data Integrity Constraints

### NOT NULL
```sql
-- Required fields
email VARCHAR(255) NOT NULL
password VARCHAR(255) NOT NULL
```

### UNIQUE
```sql
-- Prevent duplicates
email VARCHAR(255) UNIQUE
sku VARCHAR(100) UNIQUE
```

### CHECK
```sql
-- Validate data ranges
rating INTEGER CHECK (rating BETWEEN 1 AND 5)
quantity INTEGER CHECK (quantity >= 0)
price DECIMAL(10,2) CHECK (price > 0)
```

### DEFAULT
```sql
-- Default values
is_active BOOLEAN DEFAULT TRUE
created_at TIMESTAMP DEFAULT NOW()
```

---

## Timestamp Management

### Standard Timestamp Fields

Every table should have:
```sql
created_at TIMESTAMP DEFAULT NOW()
updated_at TIMESTAMP DEFAULT NOW()  -- Auto-update on change
```

### Django Implementation
```python
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
```

### Additional Timestamps (as needed)
- `deleted_at` - For soft deletes
- `verified_at` - Email verification
- `processed_at` - Payment processing
- `shipped_at`, `delivered_at` - Order tracking

---

## Soft Delete Pattern

Instead of hard deleting records, mark as deleted:

```sql
is_deleted BOOLEAN DEFAULT FALSE
deleted_at TIMESTAMP NULL
deleted_by UUID NULL
```

**Benefits:**
- Data recovery possible
- Historical records preserved
- Audit trail maintained

**Django Implementation:**
```python
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Product(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()
```

---

## Microservices Database Principles

### Database Per Service
- Each service owns its database
- No direct database access from other services
- Communication via APIs or Kafka events

### Data Ownership
- **User Service** owns user data
- **Product Service** owns product data
- **Order Service** owns order data
- **Payment Service** owns transaction data
- **Cart Service** owns cart data

### Cross-Service References
- Store IDs only, not full objects
- No foreign key constraints across databases
- Use eventual consistency via Kafka

### Example:
```python
# In Order Service - DON'T do this:
user = User.objects.get(id=order.user_id)  # Cross-service query

# DO this instead:
user_data = UserServiceClient.get_user(order.user_id)  # API call
```

---

## Performance Optimization

### Query Optimization
- Use `select_related()` for ForeignKey (single query)
- Use `prefetch_related()` for ManyToMany (minimize queries)
- Add indexes on frequently filtered fields
- Avoid N+1 query problem

### Connection Pooling
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### Database Caching
- Use Redis for frequently accessed data
- Cache query results with timeout
- Invalidate cache on data changes

---

## Security Best Practices

### Password Storage
- Never store plain text passwords
- Use Django's built-in password hashing
- Minimum password strength requirements

### Sensitive Data
- Encrypt payment tokens
- Use environment variables for credentials
- Never commit secrets to git

### SQL Injection Prevention
- Always use ORM (Django QuerySet)
- Parameterized queries
- Validate all user inputs

### Access Control
- Database users with minimal privileges
- Separate read/write users
- Audit logging for sensitive operations

---

## Monitoring & Logging

### Database Metrics
- Query execution time
- Connection pool usage
- Slow query log
- Database size growth

### Django Debug Toolbar (Development)
```python
INSTALLED_APPS = [
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
```

### Production Monitoring
- PostgreSQL: pg_stat_statements
- MongoDB: Profiler
- APM tools: New Relic, Datadog

---

## Backup & Recovery

### Backup Strategy
- **Daily full backups** - All databases
- **Hourly incremental backups** - PostgreSQL WAL
- **Point-in-time recovery** - Last 30 days
- **Offsite backups** - S3 or equivalent

### Disaster Recovery
- Recovery Time Objective (RTO): < 1 hour
- Recovery Point Objective (RPO): < 5 minutes
- Regular backup restoration tests
- Documented recovery procedures

---

## Migration Strategy

### Django Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Rollback migration
python manage.py migrate app_name migration_name
```

### Migration Best Practices
1. Small, incremental changes
2. Test migrations on staging first
3. Backup before production migration
4. Reversible migrations when possible
5. Data migrations separate from schema

### Zero-Downtime Migrations
1. Add new column (nullable)
2. Deploy code using new column
3. Backfill data
4. Make column non-nullable
5. Remove old column

---

## Testing

### Database Testing
- Use separate test database
- Fixtures for test data
- Factory Boy for model factories
- Rollback after each test

```python
from django.test import TestCase

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            first_name='Test'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
```

---

## Documentation

### What to Document
1. Schema changes (in migration files)
2. Complex queries (in code comments)
3. Business logic (in docstrings)
4. API contracts (in API docs)

### This Documentation
- Keep updated with schema changes
- Review during code reviews
- Version control with code
- Generate ER diagrams from models

---

## Summary

Following these principles ensures:
- ✅ Consistent schema design across services
- ✅ Maintainable and scalable databases
- ✅ Good performance
- ✅ Data integrity and security
- ✅ Easy to understand and modify
