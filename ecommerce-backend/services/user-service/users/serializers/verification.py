"""
Email verification serializers.
"""
from rest_framework import serializers
from django.utils import timezone

from ..models import User, EmailVerificationToken


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True, max_length=64)
    
    def validate(self, attrs):
        """Validate email and token."""
        email = attrs['email']
        token = attrs['token']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'Invalid email or token.'
            })
        
        # Check if already verified
        if user.is_verified:
            raise serializers.ValidationError({
                'email': 'Email is already verified.'
            })
        
        # Check if token exists and is valid
        try:
            verification_token = EmailVerificationToken.objects.get(
                user=user,
                token=token,
                is_used=False
            )
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError({
                'token': 'Invalid or expired token.'
            })
        
        # Check if token is expired
        if not verification_token.is_valid():
            raise serializers.ValidationError({
                'token': 'Token has expired. Please request a new verification email.'
            })
        
        # Store user and token for use in view
        attrs['user'] = user
        attrs['verification_token'] = verification_token
        
        return attrs


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending verification email."""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate that user with this email exists and is not verified."""
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security)
            raise serializers.ValidationError(
                'If an unverified account exists with this email, a verification link has been sent.'
            )
        
        if user.is_verified:
            raise serializers.ValidationError(
                'This email is already verified.'
            )
        
        return value
