# Product Service

Product Catalog microservice for the E-commerce platform.

## Features

- Product management (CRUD)
- Category management
- Product variants (size, color, etc.)
- Product images
- Product reviews and ratings
- Search and filtering
- JWT-based authentication
- Admin-only product management

## Tech Stack

- Django 5.1.2
- Django REST Framework 3.15.2
- PostgreSQL 16
- Docker & Docker Compose
- JWT Authentication (SimpleJWT)

## Setup

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Generate secrets:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))" > secrets/django_secret_key.txt
   echo "your_db_password" > secrets/db_password.txt
   ```

3. **Build and run with Docker:**
   ```bash
   docker-compose up --build
   ```

4. **Run migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser (optional):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## API Endpoints

### Public Endpoints
- `GET /api/products/` - List products
- `GET /api/products/{id}/` - Product details
- `GET /api/categories/` - List categories
- `GET /api/products/{id}/reviews/` - Product reviews

### Admin Endpoints (Requires ADMIN role)
- `POST /api/products/` - Create product
- `PUT/PATCH /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product
- `POST /api/categories/` - Create category
- Category management endpoints

## Authentication

This service validates JWT tokens issued by the User Service. The JWT secret key must match across all services.

### Required Environment Variables:
- `JWT_SECRET_KEY` - Must be same as User Service
- `ACCESS_TOKEN_LIFETIME_MINUTES` - Token expiry time
- `REFRESH_TOKEN_LIFETIME_DAYS` - Refresh token validity

## Database

PostgreSQL on port 5434 (host) → 5432 (container)

## Service Port

- Internal: 8000
- External: 8002

## Development

Run tests:
```bash
docker-compose exec web python manage.py test
```

Access Django admin:
```bash
http://localhost:8002/admin/
```

API documentation:
```bash
http://localhost:8002/api/schema/swagger-ui/
```
