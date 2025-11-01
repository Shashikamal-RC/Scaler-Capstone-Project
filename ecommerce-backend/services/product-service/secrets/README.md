# Secrets Directory

This directory contains sensitive configuration files that should NEVER be committed to version control.

## Required Files

### `django_secret_key.txt`
Django's SECRET_KEY for cryptographic signing.

**Generate:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))" > secrets/django_secret_key.txt
```

### `db_password.txt`
PostgreSQL database password.

**Create:**
```bash
echo "your_secure_password_here" > secrets/db_password.txt
```

## Security Notes

- These files are read by Docker secrets mechanism
- Never commit these files to Git (they're in `.gitignore`)
- Use different passwords for development and production
- Rotate secrets regularly in production

## File Format

- Plain text files
- No newlines or extra whitespace
- UTF-8 encoding
