"""
User views package.
Exports all views for easy import.
"""
from .auth import (
    RegisterView,
    LoginView,
    LogoutView,
)
from .profile import (
    CurrentUserView,
)
from .address import (
    UserAddressViewSet,
)

__all__ = [
    # Authentication
    'RegisterView',
    'LoginView',
    'LogoutView',
    
    # Profile
    'CurrentUserView',
    
    # Address
    'UserAddressViewSet',
]
