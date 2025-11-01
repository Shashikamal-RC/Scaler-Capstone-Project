"""
Custom JWT token classes with role information.

These custom token classes add user roles to the JWT token payload
for cross-service authentication.
"""
from rest_framework_simplejwt.tokens import RefreshToken


class CustomRefreshToken(RefreshToken):
    """
    Custom Refresh Token that includes user roles in the payload.
    
    This allows other microservices to validate user permissions
    without querying the User Service database.
    """
    
    @classmethod
    def for_user(cls, user):
        """
        Generate token for user with additional claims.
        
        Adds:
        - user_id: User's UUID
        - email: User's email
        - is_active: User's active status
        - roles: List of role names ['ADMIN', 'CUSTOMER', etc.]
        """
        token = super().for_user(user)
        
        # Add custom claims
        token['user_id'] = str(user.id)
        token['email'] = user.email
        token['is_active'] = user.is_active
        
        # Add roles as a list of role names
        roles = list(user.roles.values_list('name', flat=True))
        token['roles'] = roles
        
        return token


def generate_tokens_with_roles(user):
    """
    Generate JWT tokens with user roles included in payload.
    
    Args:
        user: User instance
        
    Returns:
        dict with 'access', 'refresh', and 'user' keys
    """
    from users.serializers.profile import UserSerializer
    
    refresh = CustomRefreshToken.for_user(user)
    
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    }
