# Shared Libraries

Common utilities and components shared across all microservices in the e-commerce platform.

## Structure

```
shared/
├── auth/                   # Authentication & Authorization
│   ├── __init__.py
│   ├── authentication.py   # JWT validation, user extraction
│   ├── permissions.py      # Role-based permission classes
│   └── README.md          # Detailed auth documentation
├── constants/             # Shared constants (future)
├── exceptions/            # Custom exception classes (future)
├── middleware/            # Common middleware (future)
└── utils/                 # Utility functions (future)
```

## Current Modules

### 🔐 Authentication & Authorization (`auth/`)

JWT token validation and role-based permissions for microservices.

**Features:**
- Cross-service JWT validation
- Role extraction from token payload
- 8+ permission classes (IsAdminUser, IsAdminOrReadOnly, etc.)
- Helper functions for role checking
- No database queries needed

**Quick Start:**
```python
from shared.auth import MicroserviceJWTAuthentication, IsAdminUser

class ProductViewSet(viewsets.ModelViewSet):
    authentication_classes = [MicroserviceJWTAuthentication]
    permission_classes = [IsAdminUser]
```

[Full Documentation](auth/README.md)

## Installation in a Service

1. **Copy shared directory** to your service root:
   ```
   your-service/
   ├── shared/           # Copy the entire shared folder here
   ├── your_app/
   ├── manage.py
   └── ...
   ```

2. **Configure settings** - Ensure JWT secret key matches User Service

3. **Import and use** - Import from `shared.auth`, `shared.utils`, etc.

## Benefits

✅ **Code Reusability** - Write once, use in all services
✅ **Consistency** - Same auth behavior across services
✅ **Maintainability** - Update in one place
✅ **Performance** - No inter-service calls for auth
✅ **Decoupling** - Services don't depend on User Service for auth

## Future Modules

### Constants (`constants/`)
- Role names
- Status codes
- Common enums

### Exceptions (`exceptions/`)
- Custom exception classes
- Error codes
- Error formatters

### Middleware (`middleware/`)
- Request logging
- Correlation IDs
- Performance monitoring

### Utils (`utils/`)
- Date/time utilities
- String helpers
- Validation functions

## Contributing

When adding new shared utilities:

1. Keep them service-agnostic
2. Document thoroughly
3. Add usage examples
4. Write unit tests
5. Update this README

## Version

Current version: 1.0.0

## Services Using This Library

- ✅ User Service (planned)
- ✅ Product Service (planned)
- 🔄 Cart Service (planned)
- 🔄 Order Service (planned)
- 🔄 Payment Service (planned)
- 🔄 Notification Service (planned)
