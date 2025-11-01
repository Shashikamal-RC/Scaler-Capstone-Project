# Shared Authentication & Authorization

Reusable authentication and permission utilities for all microservices.

## Overview

This shared library provides JWT token validation and role-based permissions that work across all services in the e-commerce platform. It eliminates the need for each service to query the User Service database for authentication.

## How It Works

1. **User Service** issues JWT tokens with user information including roles
2. **Other Services** validate the JWT token using the shared secret key
3. **User info** (id, email, roles) is extracted from the token payload
4. **Permissions** check roles without database queries

## Files

- `authentication.py` - JWT validation and user extraction
- `permissions.py` - Role-based permission classes
- `__init__.py` - Package exports

## Installation in a Service

1. **Copy shared folder** to your service root directory
2. **Configure JWT settings** in `settings.py`:

```python
# JWT Settings (MUST match User Service)
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')

SIMPLE_JWT = {
    'SIGNING_KEY': JWT_SECRET_KEY,
    'ALGORITHM': 'HS256',
    # ... other settings
}

# Use the shared authentication class
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'shared.auth.MicroserviceJWTAuthentication',
    ],
}
```

3. **Ensure shared folder is in Python path**

## Usage Examples

### Basic Authentication

```python
from rest_framework import viewsets
from shared.auth import MicroserviceJWTAuthentication, IsAdminUser

class ProductViewSet(viewsets.ModelViewSet):
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

### Admin-Only Endpoints

```python
from shared.auth import IsAdminUser

class ProductCreateView(CreateAPIView):
    permission_classes = [IsAdminUser]
    # Only users with ADMIN role can create products
```

### Read-Only for Public, Write for Admin

```python
from shared.auth import IsAdminOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    # Anyone can view categories, only admins can create/update/delete
```

### Owner or Admin Access

```python
from rest_framework.permissions import IsAuthenticated
from shared.auth import IsOwnerOrAdmin

class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    # Users can edit their own reviews, admins can edit any review
```

### Multiple Roles

```python
from shared.auth import IsManagerOrAdmin

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsManagerOrAdmin]
    # Only MANAGER or ADMIN roles can access
```

### Custom Role Check

```python
from shared.auth import HasAnyRole

class ReportView(APIView):
    permission_classes = [HasAnyRole]
    required_roles = ['ADMIN', 'MANAGER', 'SUPPORT']
    # Users with any of these roles can access
```

### Check Roles in View Logic

```python
from shared.auth import has_role, has_any_role

class MyView(APIView):
    def get(self, request):
        if has_role(request.user, 'ADMIN'):
            # Admin-specific logic
            pass
        elif has_any_role(request.user, ['MANAGER', 'SUPPORT']):
            # Manager/Support logic
            pass
```

## Available Permissions

### `IsAdminUser`
- Requires ADMIN role
- Blocks all access for non-admins

### `IsAdminOrReadOnly`
- Anyone can read (GET, HEAD, OPTIONS)
- Only ADMIN can write (POST, PUT, PATCH, DELETE)

### `IsManagerOrAdmin`
- Requires MANAGER or ADMIN role

### `IsSupportOrAdmin`
- Requires SUPPORT or ADMIN role

### `IsAuthenticatedCustomer`
- Requires CUSTOMER role
- Must be authenticated

### `IsOwnerOrAdmin`
- Owner of the object can access
- ADMIN can access any object
- Requires object to have `user_id` field

### `HasAnyRole`
- Custom roles specified in view
- Set `required_roles` attribute on view

### `ReadOnlyOrAuthenticated`
- Anyone can read
- Authenticated users can write

## Helper Functions

### `has_role(user, role_name)`
Check if user has a specific role.

```python
if has_role(request.user, 'ADMIN'):
    # User is admin
```

### `has_any_role(user, role_names)`
Check if user has any of the specified roles.

```python
if has_any_role(request.user, ['ADMIN', 'MANAGER']):
    # User is admin or manager
```

### `has_all_roles(user, role_names)`
Check if user has all of the specified roles.

```python
if has_all_roles(request.user, ['ADMIN', 'MANAGER']):
    # User is both admin and manager
```

### `get_user_from_token(token)`
Extract user info from a raw JWT token string.

```python
from shared.auth import get_user_from_token

user = get_user_from_token(token_string)
print(user.id, user.email, user.roles)
```

## Security Notes

1. **JWT Secret Key**: MUST be the same across all services
2. **Token Expiry**: Configured in User Service, enforced in all services
3. **No Database Queries**: Authentication happens via token validation only
4. **Stateless**: Each request is validated independently

## Role Names

Standard roles used in the platform:
- `ADMIN` - Full system access
- `CUSTOMER` - Regular customer access
- `MANAGER` - Management/operational access
- `SUPPORT` - Customer support access

## Troubleshooting

### "Token has expired"
- Token lifetime exceeded
- User needs to refresh token via User Service

### "Invalid token"
- Token is malformed or tampered with
- JWT secret key mismatch between services

### "Token contained no recognizable user identification"
- Token missing `user_id` field
- User Service needs to include user_id in token payload

### Permission Denied
- User doesn't have required role
- Check if roles are included in JWT token payload
- Verify User Service is adding roles to token

## Migration from SimpleJWT

If you're currently using `JWTAuthentication`:

**Before:**
```python
from rest_framework_simplejwt.authentication import JWTAuthentication

class MyView(APIView):
    authentication_classes = [JWTAuthentication]
```

**After:**
```python
from shared.auth import MicroserviceJWTAuthentication

class MyView(APIView):
    authentication_classes = [MicroserviceJWTAuthentication]
```

The new class extends SimpleJWT and adds role extraction from token payload.
