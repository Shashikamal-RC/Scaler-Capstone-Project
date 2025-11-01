#!/bin/bash

# Exit on error
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U postgres; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Read secrets
export DB_PASSWORD=$(cat $DB_PASSWORD_FILE)
export SECRET_KEY=$(cat $SECRET_KEY_FILE)

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the main command
exec "$@"
