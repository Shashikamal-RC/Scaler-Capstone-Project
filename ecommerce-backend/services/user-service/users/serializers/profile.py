"""
User profile-related serializers.
Handles user profile display and updates.
"""
from rest_framework import serializers
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Basic User serializer for profile display.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'is_active', 'is_verified', 'roles',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_active', 'is_verified', 'created_at', 'updated_at']
    
    def get_roles(self, obj):
        """Get user roles as a list of role names."""
        return [role.name for role in obj.roles.all()]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    Allows updating basic profile information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']
    
    def validate_phone_number(self, value):
        """Validate phone number uniqueness (excluding current user)."""
        user = self.instance
        if value and User.objects.filter(phone_number=value).exclude(id=user.id).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )
        return value
