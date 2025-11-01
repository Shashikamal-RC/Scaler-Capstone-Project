# User Service - E-Commerce Microservices

User Service is responsible for user authentication, authorization, and profile management in the e-commerce platform.

## 📋 Features

- ✅ User registration and authentication
- ✅ JWT-based authorization
- ✅ Role-based access control (RBAC)
- ✅ User profile management
- ✅ Multiple address management
- ✅ Password reset functionality
- ✅ RESTful API with Django REST Framework
- ✅ API documentation with drf-spectacular

## 🛠️ Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Django | 5.1.2 | Web framework |
| Django REST Framework | 3.15.2 | REST API |
| PostgreSQL | 16.x | Database |
| JWT | 5.3.1 | Authentication |
| Argon2 | 23.1.0 | Password hashing |

## 📁 Project Structure

```
user-service/
├── manage.py                   # Django management script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
├── .env.example              # Environment template
├── user_service/             # Django project
│   ├── settings.py          # Project settings
│   ├── urls.py              # URL configuration
│   ├── wsgi.py              # WSGI config
│   └── asgi.py              # ASGI config
├── users/                    # Users app
│   ├── models.py            # Database models
│   ├── views.py             # API views
│   ├── serializers.py       # DRF serializers
│   ├── urls.py              # App URLs
│   └── migrations/          # Database migrations
├── static/                   # Static files
├── media/                    # User uploads
├── logs/                     # Application logs
└── templates/                # HTML templates
```

## ⚙️ Setup Instructions

### Option 1: Docker Setup (Recommended)

**Prerequisites:**
- Docker Desktop installed
- Docker Compose installed

**Steps:**

1. **Clone Repository**
```bash
cd ecommerce-backend/services/user-service
```

2. **Build and Run with Docker Compose**
```bash
docker-compose up --build
```

This will:
- Create PostgreSQL database container
- Create Django application container
- Run migrations automatically
- Create default superuser (admin@example.com / admin123)
- Create default roles (CUSTOMER, ADMIN, MANAGER)
- Start the development server at `http://localhost:8000`

3. **Access the Application**
- API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`
- API Docs: `http://localhost:8000/api/docs/`

**Docker Commands:**

```bash
# Start services
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f web

# Run Django commands
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# Rebuild containers
docker-compose up --build

# Remove volumes (clean database)
docker-compose down -v
```

---

### Option 2: Local Setup

**Prerequisites:**

- Python 3.12+
- PostgreSQL 16.x
- pip (Python package manager)

### 1. Clone Repository

```bash
cd ecommerce-backend/services/user-service
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create `.env` file from template:

```bash
cp .env.example .env
```

Update `.env` with your configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=user_service_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Database Setup

Create PostgreSQL database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE user_service_db;

# Create user (optional)
CREATE USER user_service_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE user_service_db TO user_service_user;
\q
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Server will start at: `http://127.0.0.1:8000/`

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register/` | User registration |
| POST | `/api/users/login/` | User login |
| POST | `/api/users/token/refresh/` | Refresh JWT token |
| POST | `/api/users/logout/` | User logout |

### User Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/profile/` | Get user profile |
| PUT | `/api/users/profile/` | Update profile |
| PATCH | `/api/users/profile/` | Partial update |

### Addresses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/addresses/` | List all addresses |
| POST | `/api/users/addresses/` | Add new address |
| GET | `/api/users/addresses/{id}/` | Get address details |
| PUT | `/api/users/addresses/{id}/` | Update address |
| DELETE | `/api/users/addresses/{id}/` | Delete address |

### Password Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/password/change/` | Change password |
| POST | `/api/users/password/reset/` | Request password reset |
| POST | `/api/users/password/reset/confirm/` | Confirm password reset |

## 📚 API Documentation

Interactive API documentation available at:

- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **ReDoc**: `http://127.0.0.1:8000/api/redoc/`
- **OpenAPI Schema**: `http://127.0.0.1:8000/api/schema/`

## 🗄️ Database Schema

### Tables

1. **users** - Main user table with authentication
2. **user_roles** - Role definitions (CUSTOMER, ADMIN, MANAGER)
3. **user_role_mapping** - Many-to-many user-role relationship
4. **user_addresses** - User shipping/billing addresses
5. **password_reset_tokens** - Password reset token management

See `docs/database/user-service-schema.md` for complete schema.

## 🧪 Testing

Run tests:

```bash
# All tests
python manage.py test

# Specific app
python manage.py test users

# With coverage
coverage run manage.py test
coverage report
```

## 📝 Django Admin

Access Django admin at: `http://127.0.0.1:8000/admin/`

Use superuser credentials created earlier.

## 🔒 Security Features

- ✅ Argon2 password hashing
- ✅ JWT token authentication
- ✅ CORS configuration
- ✅ HTTPS enforcement (production)
- ✅ Security middleware
- ✅ Rate limiting (planned)

## 📊 Logging

Logs are stored in `logs/user_service.log`

Log levels:
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- DEBUG: Detailed debug information (development only)

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL with SSL
- [ ] Configure Redis for caching
- [ ] Set up Gunicorn/uWSGI
- [ ] Configure Nginx reverse proxy
- [ ] Set up SSL certificates
- [ ] Configure monitoring
- [ ] Set up backup strategy

## 🛠️ Development Commands

```bash
# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run shell
python manage.py shell

# Check for issues
python manage.py check
```

## 📦 Dependencies

See `requirements.txt` for full list.

Main dependencies:
- Django 5.1.2
- djangorestframework 3.15.2
- psycopg2-binary 2.9.9
- djangorestframework-simplejwt 5.3.1
- django-cors-headers 4.4.0
- python-decouple 3.8
- argon2-cffi 23.1.0
- drf-spectacular 0.27.2

## 🤝 Contributing

1. Create feature branch
2. Write tests
3. Update documentation
4. Submit pull request

## 📄 License

Part of Scaler Neovarsity Capstone Project

---

**Author**: Shashikamal RC  
**Guide**: Naman Bhalla  
**Institution**: Scaler Neovarsity - Woolf  
**Year**: 2025
