#!/bin/sh

# Exit on error
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Creating migrations..."
python manage.py makemigrations --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if not exists..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print("Superuser created: admin@example.com / admin123")
else:
    print("Superuser already exists")
EOF

echo "Creating default roles..."
python manage.py shell << EOF
from users.models import UserRole
roles = ['CUSTOMER', 'ADMIN', 'MANAGER']
for role_name in roles:
    role, created = UserRole.objects.get_or_create(
        name=role_name,
        defaults={'description': f'{role_name.capitalize()} role'}
    )
    if created:
        print(f"Role created: {role_name}")
    else:
        print(f"Role already exists: {role_name}")
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
