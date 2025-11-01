"""
Authentication-related serializers.
Handles user registration, login, and token generation.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from ..models import User, UserRole
from ..tokens import generate_tokens_with_roles


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates input and creates new user with CUSTOMER role.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness (case-insensitive)."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value.lower()
    
    def validate_phone_number(self, value):
        """Validate phone number uniqueness if provided."""
        if value and User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "A user with this phone number already exists."
            )
        return value
    
    def create(self, validated_data):
        """
        Create user with hashed password and assign CUSTOMER role.
        """
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        
        # Create user with hashed password
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number'),
        )
        
        # Assign CUSTOMER role by default
        customer_role, created = UserRole.objects.get_or_create(
            name=UserRole.RoleChoices.CUSTOMER,
            defaults={'description': 'Regular customer'}
        )
        user.roles.add(customer_role)
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials and returns JWT tokens.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Authenticate user and generate tokens."""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError(
                "Must include 'email' and 'password'."
            )
        
        # Authenticate user
        user = authenticate(
            request=self.context.get('request'),
            username=email,  # Our USERNAME_FIELD is email
            password=password
        )
        
        if not user:
            raise serializers.ValidationError(
                "Invalid email or password."
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                "User account is disabled."
            )
        
        # Store user in validated data for view to access
        attrs['user'] = user
        return attrs


class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer for JWT token response.
    Returns access token, refresh token, and user data.
    """
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """Get user data using UserSerializer."""
        from .profile import UserSerializer
        return UserSerializer(obj.get('user')).data


def generate_tokens_for_user(user):
    """
    Helper function to generate JWT tokens for a user with roles.
    Returns dict with access token, refresh token, and user data.
    
    DEPRECATED: Use generate_tokens_with_roles from users.tokens instead.
    This is kept for backward compatibility.
    """
    return generate_tokens_with_roles(user)
