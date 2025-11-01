"""
Admin-related serializers for user management.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from ..models import User, UserRole, UserRoleMapping


class AdminUserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (admin view)."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    roles = serializers.SerializerMethodField()
    address_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'is_active', 'is_verified', 'is_staff',
            'roles', 'address_count', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']
    
    def get_roles(self, obj):
        """Get list of role names for the user."""
        return [role.name for role in obj.roles.all()]
    
    def get_address_count(self, obj):
        """Get count of user addresses."""
        return obj.addresses.count()


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single user (admin view)."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    roles = serializers.SerializerMethodField()
    address_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'is_active', 'is_verified', 'is_staff', 'is_superuser',
            'roles', 'address_count', 'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']
    
    def get_roles(self, obj):
        """Get detailed role information."""
        return [
            {
                'id': str(role.id),
                'name': role.name,
                'description': role.description
            }
            for role in obj.roles.all()
        ]
    
    def get_address_count(self, obj):
        """Get count of user addresses."""
        return obj.addresses.count()


class RoleAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning/removing roles."""
    role_name = serializers.ChoiceField(
        choices=[choice[0] for choice in UserRole.RoleChoices.choices],
        required=True
    )
    
    def validate_role_name(self, value):
        """Validate that role exists."""
        try:
            UserRole.objects.get(name=value)
        except UserRole.DoesNotExist:
            raise serializers.ValidationError(f"Role '{value}' does not exist.")
        return value


class UserStatusSerializer(serializers.Serializer):
    """Serializer for activating/deactivating users."""
    is_active = serializers.BooleanField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """Serializer for admin creating users."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    roles = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[choice[0] for choice in UserRole.RoleChoices.choices]
        ),
        required=False,
        default=['CUSTOMER']
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'first_name', 'last_name', 
            'phone_number', 'is_active', 'is_verified', 'is_staff', 'roles'
        ]
    
    def create(self, validated_data):
        """Create user with specified roles."""
        roles_data = validated_data.pop('roles', ['CUSTOMER'])
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number'),
            is_active=validated_data.get('is_active', True),
            is_verified=validated_data.get('is_verified', False),
            is_staff=validated_data.get('is_staff', False),
        )
        
        # Assign roles
        for role_name in roles_data:
            role, _ = UserRole.objects.get_or_create(
                name=role_name,
                defaults={'description': f'{role_name} role'}
            )
            user.roles.add(role)
        
        return user
