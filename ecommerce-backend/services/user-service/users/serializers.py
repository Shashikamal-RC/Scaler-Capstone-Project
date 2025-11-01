from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserRole, UserAddress


# ==============================================================================
# USER SERIALIZER (Basic)
# ==============================================================================

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


# ==============================================================================
# REGISTER SERIALIZER
# ==============================================================================

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


# ==============================================================================
# LOGIN SERIALIZER
# ==============================================================================

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


# ==============================================================================
# TOKEN RESPONSE SERIALIZER
# ==============================================================================

class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer for JWT token response.
    Returns access token, refresh token, and user data.
    """
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)


def generate_tokens_for_user(user):
    """
    Helper function to generate JWT tokens for a user.
    Returns dict with access token, refresh token, and user data.
    """
    refresh = RefreshToken.for_user(user)
    
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    }


# ==============================================================================
# USER UPDATE SERIALIZER
# ==============================================================================

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
