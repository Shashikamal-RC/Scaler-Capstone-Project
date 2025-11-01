"""
Shared Authentication Utilities for Microservices.

This module provides JWT token validation and user authentication
that can be shared across all microservices in the e-commerce platform.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt


class MicroserviceJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication for microservices.
    
    Validates JWT tokens issued by the User Service and extracts
    user information including roles from the token payload.
    """
    
    def get_validated_token(self, raw_token):
        """
        Validates the JWT token using the shared secret key.
        
        Args:
            raw_token: The raw JWT token string
            
        Returns:
            Validated token payload
            
        Raises:
            InvalidToken: If token is invalid or expired
        """
        try:
            # Validate token using shared JWT secret
            payload = jwt.decode(
                raw_token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise InvalidToken('Token has expired')
        except jwt.InvalidTokenError as e:
            raise InvalidToken(f'Invalid token: {str(e)}')
    
    def get_user(self, validated_token):
        """
        Extract user information from validated token.
        
        Creates a lightweight user object with information from the JWT payload.
        This avoids querying the User Service database from other services.
        
        Args:
            validated_token: The validated JWT token payload
            
        Returns:
            User object with id, email, and roles
        """
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Token contained no recognizable user identification')
            
            # Create a simple user object from token data
            user = type('User', (), {
                'id': user_id,
                'email': validated_token.get('email', ''),
                'is_authenticated': True,
                'is_active': validated_token.get('is_active', True),
                'roles': validated_token.get('roles', []),  # List of role names
            })()
            
            return user
            
        except KeyError:
            raise AuthenticationFailed('Token contained incomplete user data')


def has_role(user, role_name):
    """
    Check if user has a specific role.
    
    Args:
        user: User object from JWT token
        role_name: Name of the role to check (e.g., 'ADMIN', 'CUSTOMER')
        
    Returns:
        Boolean indicating if user has the role
    """
    if not hasattr(user, 'roles'):
        return False
    return role_name in user.roles


def has_any_role(user, role_names):
    """
    Check if user has any of the specified roles.
    
    Args:
        user: User object from JWT token
        role_names: List of role names to check
        
    Returns:
        Boolean indicating if user has any of the roles
    """
    if not hasattr(user, 'roles'):
        return False
    return any(role in user.roles for role in role_names)


def has_all_roles(user, role_names):
    """
    Check if user has all of the specified roles.
    
    Args:
        user: User object from JWT token
        role_names: List of role names to check
        
    Returns:
        Boolean indicating if user has all the roles
    """
    if not hasattr(user, 'roles'):
        return False
    return all(role in user.roles for role in role_names)


def get_user_from_token(token):
    """
    Extract user information directly from a JWT token string.
    
    Useful for background tasks or when you have a raw token.
    
    Args:
        token: JWT token string
        
    Returns:
        User object with information from token
        
    Raises:
        InvalidToken: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SIMPLE_JWT['SIGNING_KEY'],
            algorithms=[settings.SIMPLE_JWT['ALGORITHM']]
        )
        
        user = type('User', (), {
            'id': payload.get('user_id'),
            'email': payload.get('email', ''),
            'is_authenticated': True,
            'is_active': payload.get('is_active', True),
            'roles': payload.get('roles', []),
        })()
        
        return user
        
    except jwt.InvalidTokenError as e:
        raise InvalidToken(f'Invalid token: {str(e)}')
