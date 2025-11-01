"""
Password management serializers.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from ..models import User, PasswordResetToken


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset."""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate that user with this email exists."""
        if not User.objects.filter(email=value).exists():
            # Don't reveal if email exists or not (security)
            # Return success regardless to prevent email enumeration
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset with token."""
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True, max_length=64)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate passwords match and token is valid."""
        # Check passwords match
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        
        # Validate password strength
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        # Validate token
        email = attrs['email']
        token = attrs['token']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'Invalid email or token.'
            })
        
        # Check if token exists and is valid
        expiry_time = timezone.now() - timedelta(
            hours=settings.PASSWORD_RESET_TOKEN_EXPIRY_HOURS
        )
        
        try:
            reset_token = PasswordResetToken.objects.get(
                user=user,
                token=token,
                is_used=False,
                created_at__gte=expiry_time
            )
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({
                'token': 'Invalid or expired token.'
            })
        
        # Store user and token for use in view
        attrs['user'] = user
        attrs['reset_token'] = reset_token
        
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password (authenticated user)."""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Validate old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
    
    def validate(self, attrs):
        """Validate new passwords match."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        
        # Validate password strength
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        # Check new password is different from old
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({
                'new_password': 'New password must be different from current password.'
            })
        
        return attrs
