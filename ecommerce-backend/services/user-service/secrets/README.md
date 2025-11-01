# Secrets Directory

This directory contains sensitive files used by Docker secrets.

**⚠️ SECURITY WARNING: NEVER commit secret files to Git!**

## Files

- `db_password.txt` - PostgreSQL database password
- `django_secret_key.txt` - Django SECRET_KEY for cryptographic signing

## Usage

These files are mounted as Docker secrets and accessed by containers at runtime.

## Setup

1. **Development**: Use the provided example secrets (not secure, for dev only)
2. **Production**: 
   - Generate strong random values
   - Use external secret management (AWS Secrets Manager, HashiCorp Vault, etc.)
   - Or use encrypted secrets in CI/CD pipeline

## Generating Secure Values

### Django Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Database Password
```bash
# Linux/Mac
openssl rand -base64 32

# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

## Production Best Practices

1. **Never commit secrets to version control**
2. **Use different secrets per environment**
3. **Rotate secrets regularly**
4. **Use secret management services in production**
5. **Limit access with file permissions** (chmod 600 on Linux/Mac)