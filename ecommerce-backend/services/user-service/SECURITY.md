# Security Configuration Guide

## Overview

This User Service implements production-grade security using Docker secrets, secure environment management, and industry best practices.

## Security Features Implemented

### 1. **Docker Secrets** 🔐
- Sensitive values stored in separate files (not in code or compose file)
- Secrets mounted at runtime via `/run/secrets/`
- Files excluded from Git via `.gitignore`

**Secrets managed:**
- `db_password` - PostgreSQL password
- `django_secret_key` - Django SECRET_KEY for cryptographic operations

### 2. **Environment Separation** 🏗️
- Development: `docker-compose.yml` with `.env`
- Production: `docker-compose.prod.yml` override with strict security

### 3. **Network Security** 🌐
- Isolated Docker network
- Database not exposed to host in production
- CORS configured with specific origins

### 4. **Application Security** 🛡️
- HTTPS enforcement in production
- Secure cookies (HTTPS only)
- HSTS (HTTP Strict Transport Security)
- XSS protection
- Clickjacking protection
- Argon2 password hashing

### 5. **Database Security** 💾
- Connection pooling
- Prepared statements (Django ORM)
- Strong password requirements
- PostgreSQL latest security patches

## File Structure

```
user-service/
├── secrets/                    # Docker secrets (NEVER commit!)
│   ├── .gitignore             # Excludes all secret files
│   ├── README.md              # Secret management guide
│   ├── db_password.txt        # PostgreSQL password
│   └── django_secret_key.txt  # Django SECRET_KEY
├── .env                        # Non-sensitive environment vars
├── .env.example               # Template for setup
├── docker-compose.yml         # Development configuration
├── docker-compose.prod.yml    # Production overrides
└── SECURITY.md                # This file
```

## Setup Instructions

### Development Environment

1. **Generate secrets** (first time only):
```powershell
# Generate Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" > secrets/django_secret_key.txt

# Generate database password
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_}) > secrets/db_password.txt
```

2. **Start services**:
```powershell
docker compose up -d
```

### Production Environment

1. **Update secrets with strong values**:
```powershell
# Use a password manager or secret generation service
# Example: AWS Secrets Manager, HashiCorp Vault, 1Password

# Generate strong Django secret key (50+ characters)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" > secrets/django_secret_key.txt

# Generate strong database password (32+ characters, mixed case, numbers, symbols)
openssl rand -base64 32 > secrets/db_password.txt
```

2. **Update production settings** in `docker-compose.prod.yml`:
   - Set correct `ALLOWED_HOSTS`
   - Configure SSL certificates
   - Set up reverse proxy (Nginx/Traefik)

3. **Deploy with production config**:
```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## How Secrets Work

### Flow Diagram
```
┌─────────────────────┐
│ secrets/*.txt files │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│ Docker Compose reads files  │
│ and mounts as secrets       │
└──────────┬──────────────────┘
           │
           ▼
┌────────────────────────────────┐
│ Container: /run/secrets/       │
│   - db_password (read-only)    │
│   - django_secret_key (read)   │
└──────────┬─────────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Django settings.py           │
│ read_secret() function reads │
│ from /run/secrets/ files     │
└──────────┬───────────────────┘
           │
           ▼
┌─────────────────────────┐
│ Application uses values │
└─────────────────────────┘
```

### Code Implementation

**docker-compose.yml:**
```yaml
services:
  web:
    environment:
      - SECRET_KEY_FILE=/run/secrets/django_secret_key
      - DB_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - django_secret_key
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
  django_secret_key:
    file: ./secrets/django_secret_key.txt
```

**settings.py:**
```python
def read_secret(secret_name, default=None):
    """Read Docker secret from file, fall back to env var, then default."""
    secret_file = os.getenv(f'{secret_name}_FILE')
    if secret_file and os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            return f.read().strip()
    return os.getenv(secret_name, config(secret_name, default=default))

SECRET_KEY = read_secret('SECRET_KEY')
DB_PASSWORD = read_secret('DB_PASSWORD')
```

## Security Checklist

### Development ✅
- [x] Secrets stored in separate files
- [x] Secrets excluded from Git
- [x] Django DEBUG=True for development
- [x] Database exposed on localhost for debugging

### Production 🔒
- [ ] Generate strong secrets (32+ characters)
- [ ] Set DEBUG=False
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Enable HTTPS/SSL
- [ ] Use reverse proxy (Nginx/Traefik)
- [ ] Don't expose database port to host
- [ ] Set up monitoring and logging
- [ ] Configure backups
- [ ] Use external secret management (AWS Secrets Manager, Vault)
- [ ] Enable rate limiting
- [ ] Set up Web Application Firewall (WAF)
- [ ] Regular security updates
- [ ] Penetration testing

## Best Practices

### 1. **Secret Rotation** 🔄
Rotate secrets regularly:
- Database passwords: Every 90 days
- Django SECRET_KEY: Every 180 days (requires user re-login)
- API keys: Per vendor recommendations

### 2. **Access Control** 🔐
```powershell
# Restrict file permissions (Linux/Mac)
chmod 600 secrets/*.txt
chmod 700 secrets/

# On Windows, use file properties to restrict access
```

### 3. **Never Commit Secrets** ⛔
```bash
# Check what would be committed
git status

# Verify secrets are ignored
git check-ignore secrets/*.txt

# Scan for accidentally committed secrets
git log -p | grep -i "password\|secret\|key"
```

### 4. **Environment-Specific Secrets** 🌍
- Development: Simple secrets (already provided)
- Staging: Similar to production, but isolated
- Production: Strong, unique secrets, managed externally

### 5. **Monitoring & Alerts** 📊
Set up alerts for:
- Failed login attempts
- Secret access patterns
- Configuration changes
- Database connection errors

## External Secret Management (Recommended for Production)

### AWS Secrets Manager
```yaml
# docker-compose.prod.yml
secrets:
  db_password:
    external: true
    name: user_service_db_password
```

### HashiCorp Vault
```python
# settings.py
import hvac
client = hvac.Client(url='https://vault.example.com')
SECRET_KEY = client.secrets.kv.v2.read_secret_version(path='user-service/django')['data']['secret_key']
```

### Kubernetes Secrets (for K8s deployment)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: user-service-secrets
type: Opaque
data:
  db-password: <base64-encoded>
  django-secret-key: <base64-encoded>
```

## Compliance & Standards

This implementation follows:
- ✅ **OWASP Top 10** security recommendations
- ✅ **12-Factor App** methodology
- ✅ **PCI-DSS** for payment processing (when applicable)
- ✅ **GDPR** data protection principles
- ✅ **ISO 27001** information security standards

## Incident Response

If secrets are compromised:

1. **Immediate actions:**
   - Rotate all affected secrets
   - Force logout all users (if SECRET_KEY compromised)
   - Review access logs
   - Notify security team

2. **Investigation:**
   - Check Git history
   - Review container logs
   - Audit file access
   - Check for unauthorized access

3. **Prevention:**
   - Update `.gitignore`
   - Implement secret scanning in CI/CD
   - Review access controls
   - Train team on security practices

## Support

For security concerns:
- Internal: Contact your security team
- External: Follow responsible disclosure process

## References

- [Django Security](https://docs.djangoproject.com/en/5.1/topics/security/)
- [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/)
- [OWASP Security Guidelines](https://owasp.org/)
- [12-Factor App](https://12factor.net/)