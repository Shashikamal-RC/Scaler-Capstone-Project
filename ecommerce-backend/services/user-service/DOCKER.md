# Docker Setup Guide for User Service

## Prerequisites

1. **Docker Desktop** installed and running
2. Docker Compose (included with Docker Desktop)

## Quick Start

### 1. Start Docker Desktop
Make sure Docker Desktop is running on your system.

### 2. Build and Run Containers

```powershell
# Navigate to user-service directory
cd ecommerce-backend\services\user-service

# Build and start containers
docker compose up --build -d
```

### 3. Check Container Status

```powershell
# View running containers
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f web
docker compose logs -f db
```

## What Gets Created

### Containers
- **user_service_db** - PostgreSQL 16 database
- **user_service_web** - Django application

### Volumes
- **postgres_data** - Persistent database storage
- **static_volume** - Static files
- **media_volume** - User uploaded files
- **logs_volume** - Application logs

### Network
- **user_service_network** - Bridge network for service communication

## Accessing Services

- **Django API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs
- **PostgreSQL**: localhost:5432

## Default Credentials

### Superuser (Django Admin)
- **Email**: admin@example.com
- **Password**: admin123

### PostgreSQL
- **Database**: user_service_db
- **User**: postgres
- **Password**: postgres
- **Host**: localhost (or `db` from within containers)
- **Port**: 5432

## Automatic Setup

The entrypoint script automatically:
1. ✅ Waits for PostgreSQL to be ready
2. ✅ Runs database migrations
3. ✅ Creates default superuser (admin@example.com)
4. ✅ Creates default roles (CUSTOMER, ADMIN, MANAGER)
5. ✅ Collects static files
6. ✅ Starts Django server

## Common Commands

### Stop Containers
```powershell
docker compose down
```

### Stop and Remove Volumes (Clean Start)
```powershell
docker compose down -v
```

### Restart Containers
```powershell
docker compose restart
```

### View Container Logs
```powershell
# All services
docker compose logs -f

# Only web service
docker compose logs -f web

# Only database
docker compose logs -f db
```

### Execute Commands in Container
```powershell
# Access Django shell
docker compose exec web python manage.py shell

# Create superuser manually
docker compose exec web python manage.py createsuperuser

# Run migrations
docker compose exec web python manage.py migrate

# Access PostgreSQL shell
docker compose exec db psql -U postgres -d user_service_db
```

### Rebuild Containers
```powershell
# Rebuild after code changes
docker compose up --build

# Force rebuild
docker compose build --no-cache
docker compose up -d
```

## Development Workflow

### 1. Make Code Changes
Edit your Python files locally. Changes are automatically reflected in the container due to volume mounting.

### 2. Run Migrations After Model Changes
```powershell
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### 3. Install New Python Package
```powershell
# Add package to requirements.txt first, then:
docker compose exec web pip install -r requirements.txt

# Or rebuild container
docker compose up --build
```

## Troubleshooting

### Container Won't Start
```powershell
# Check logs
docker compose logs web

# Check if port is already in use
netstat -ano | findstr :8000
netstat -ano | findstr :5432
```

### Database Connection Error
```powershell
# Check database is running
docker compose ps db

# Check database logs
docker compose logs db

# Restart database
docker compose restart db
```

### Permission Issues (Linux/Mac)
```bash
# Fix permissions
sudo chown -R $USER:$USER .
chmod +x entrypoint.sh
```

### Reset Everything
```powershell
# Stop and remove everything
docker compose down -v

# Remove Docker images
docker compose down --rmi all

# Rebuild from scratch
docker compose up --build
```

## Production Deployment

### Environment Variables
Create a `.env.production` file:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DB_PASSWORD=strong-production-password
```

### Use Production Compose File
```powershell
docker compose -f docker-compose.prod.yml up -d
```

### Security Checklist
- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Update ALLOWED_HOSTS
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure backups
- [ ] Use Docker secrets for sensitive data

## Monitoring

### Container Health
```powershell
# Check health status
docker compose ps

# View resource usage
docker stats
```

### Database Backup
```powershell
# Backup database
docker compose exec db pg_dump -U postgres user_service_db > backup.sql

# Restore database
docker compose exec -T db psql -U postgres user_service_db < backup.sql
```

## Clean Up

### Remove Containers Only
```powershell
docker compose down
```

### Remove Containers and Volumes
```powershell
docker compose down -v
```

### Remove Everything (Images too)
```powershell
docker compose down -v --rmi all
```

## Next Steps

1. Start Docker Desktop
2. Run `docker compose up --build -d`
3. Access http://localhost:8000/admin
4. Login with admin@example.com / admin123
5. Start developing! 🚀
