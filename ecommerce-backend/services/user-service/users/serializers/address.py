"""
Address-related serializers.
Handles user address management.
"""
from rest_framework import serializers
from ..models import UserAddress


class UserAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for UserAddress display.
    """
    address_type_display = serializers.CharField(
        source='get_address_type_display',
        read_only=True
    )
    full_address = serializers.CharField(
        source='get_full_address',
        read_only=True
    )
    
    class Meta:
        model = UserAddress
        fields = [
            'id', 'address_type', 'address_type_display', 'full_name',
            'phone_number', 'address_line1', 'address_line2', 'city',
            'state', 'postal_code', 'country', 'is_default',
            'full_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserAddressCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating UserAddress.
    """
    
    class Meta:
        model = UserAddress
        fields = [
            'address_type', 'full_name', 'phone_number',
            'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'is_default'
        ]
    
    def create(self, validated_data):
        """Create address for the authenticated user."""
        user = self.context['request'].user
        return UserAddress.objects.create(user=user, **validated_data)
    
    def validate(self, attrs):
        """Validate address data."""
        # Ensure at least one field is provided for update
        if self.instance and not attrs:
            raise serializers.ValidationError(
                "At least one field must be provided for update."
            )
        return attrs
