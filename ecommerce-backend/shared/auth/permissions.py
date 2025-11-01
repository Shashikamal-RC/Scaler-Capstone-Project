"""
Shared Permission Classes for Microservices.

Custom permission classes that work with JWT tokens containing role information.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .authentication import has_role, has_any_role


class IsAdminUser(BasePermission):
    """
    Permission class to allow only users with ADMIN role.
    
    Usage:
        class ProductViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAdminUser]
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has ADMIN role."""
        if not request.user or not request.user.is_authenticated:
            return False
        return has_role(request.user, 'ADMIN')


class IsAdminOrReadOnly(BasePermission):
    """
    Permission class to allow ADMIN full access, others read-only.
    
    Useful for public resources that only admins can modify.
    
    Usage:
        class CategoryViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAdminOrReadOnly]
    """
    
    def has_permission(self, request, view):
        """Allow GET/HEAD/OPTIONS for anyone, POST/PUT/PATCH/DELETE for admins only."""
        if request.method in SAFE_METHODS:
            return True
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        return has_role(request.user, 'ADMIN')


class IsManagerOrAdmin(BasePermission):
    """
    Permission class to allow MANAGER or ADMIN roles.
    
    Usage:
        class OrderViewSet(viewsets.ModelViewSet):
            permission_classes = [IsManagerOrAdmin]
    """
    
    def has_permission(self, request, view):
        """Check if user has MANAGER or ADMIN role."""
        if not request.user or not request.user.is_authenticated:
            return False
        return has_any_role(request.user, ['ADMIN', 'MANAGER'])


class IsOwnerOrAdmin(BasePermission):
    """
    Permission class to allow object owner or admin to access.
    
    Requires the object to have a 'user_id' field.
    
    Usage:
        class ReviewViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the owner of the object or an admin.
        
        For objects with user_id field (from User Service).
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin can access everything
        if has_role(request.user, 'ADMIN'):
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user_id'):
            return str(obj.user_id) == str(request.user.id)
        
        return False


class IsAuthenticatedCustomer(BasePermission):
    """
    Permission class to allow authenticated users with CUSTOMER role.
    
    Usage:
        class CartViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticatedCustomer]
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has CUSTOMER role."""
        if not request.user or not request.user.is_authenticated:
            return False
        return has_role(request.user, 'CUSTOMER')


class IsSupportOrAdmin(BasePermission):
    """
    Permission class to allow SUPPORT or ADMIN roles.
    
    Useful for customer support endpoints.
    
    Usage:
        class TicketViewSet(viewsets.ModelViewSet):
            permission_classes = [IsSupportOrAdmin]
    """
    
    def has_permission(self, request, view):
        """Check if user has SUPPORT or ADMIN role."""
        if not request.user or not request.user.is_authenticated:
            return False
        return has_any_role(request.user, ['ADMIN', 'SUPPORT'])


class HasAnyRole(BasePermission):
    """
    Permission class that checks if user has any of the specified roles.
    
    Usage:
        class MyView(APIView):
            permission_classes = [HasAnyRole]
            required_roles = ['ADMIN', 'MANAGER', 'SUPPORT']
    """
    
    def has_permission(self, request, view):
        """Check if user has any of the required roles."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get required roles from view
        required_roles = getattr(view, 'required_roles', [])
        if not required_roles:
            return True
        
        return has_any_role(request.user, required_roles)


class ReadOnlyOrAuthenticated(BasePermission):
    """
    Permission class to allow read-only for anyone, write for authenticated users.
    
    Usage:
        class ProductReviewViewSet(viewsets.ModelViewSet):
            permission_classes = [ReadOnlyOrAuthenticated]
    """
    
    def has_permission(self, request, view):
        """Allow safe methods for anyone, write methods for authenticated users."""
        if request.method in SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated
