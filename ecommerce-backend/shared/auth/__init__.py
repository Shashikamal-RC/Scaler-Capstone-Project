"""
Shared Authentication and Authorization Package.

This package provides reusable authentication and permission utilities
for all microservices in the e-commerce platform.

Usage in any service:
    from shared.auth.authentication import MicroserviceJWTAuthentication
    from shared.auth.permissions import IsAdminUser, IsAdminOrReadOnly
    
    class ProductViewSet(viewsets.ModelViewSet):
        authentication_classes = [MicroserviceJWTAuthentication]
        permission_classes = [IsAdminUser]
"""

from .authentication import (
    MicroserviceJWTAuthentication,
    has_role,
    has_any_role,
    has_all_roles,
    get_user_from_token,
)

from .permissions import (
    IsAdminUser,
    IsAdminOrReadOnly,
    IsManagerOrAdmin,
    IsOwnerOrAdmin,
    IsAuthenticatedCustomer,
    IsSupportOrAdmin,
    HasAnyRole,
    ReadOnlyOrAuthenticated,
)

__all__ = [
    # Authentication
    'MicroserviceJWTAuthentication',
    'has_role',
    'has_any_role',
    'has_all_roles',
    'get_user_from_token',
    
    # Permissions
    'IsAdminUser',
    'IsAdminOrReadOnly',
    'IsManagerOrAdmin',
    'IsOwnerOrAdmin',
    'IsAuthenticatedCustomer',
    'IsSupportOrAdmin',
    'HasAnyRole',
    'ReadOnlyOrAuthenticated',
]
