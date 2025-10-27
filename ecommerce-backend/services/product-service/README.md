# Product Service

## Purpose
Manages product catalog, categories, and inventory.

## Responsibilities
- Product CRUD operations
- Category management
- Product search (with Elasticsearch)
- Inventory tracking
- Product filtering and pagination

## Database
- PostgreSQL
- Tables: Products, Categories, Inventory

## Search Engine
- Elasticsearch for fast product search

## APIs (To be implemented)
- GET `/api/products` - List all products (with filters)
- GET `/api/products/:id` - Get product details
- POST `/api/products` - Create product (Admin)
- PUT `/api/products/:id` - Update product (Admin)
- DELETE `/api/products/:id` - Delete product (Admin)
- GET `/api/categories` - List all categories
- GET `/api/products/search` - Search products

## Kafka Events (Producer)
- `product.created` - When new product is added
- `product.updated` - When product is updated
- `product.deleted` - When product is deleted
- `inventory.low` - When inventory is low
