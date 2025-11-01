"""
Password management views.
Handles password reset and change operations.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
import secrets

from ..models import User, PasswordResetToken
from ..serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
)
from ..utils import send_password_reset_email, send_password_changed_notification


class PasswordResetRequestView(APIView):
    """
    Request password reset - sends reset token to email.
    POST /api/auth/password-reset-request/
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(description="Password reset email sent successfully"),
            400: OpenApiResponse(description="Bad Request")
        },
        tags=['Authentication'],
        description="Request password reset. Sends reset token to user's email if account exists."
    )
    def post(self, request):
        """Request password reset."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Always return success to prevent email enumeration
        try:
            user = User.objects.get(email=email)
            
            # Invalidate old tokens
            PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).update(is_used=True)
            
            # Generate new token
            token = secrets.token_urlsafe(32)
            
            # Create password reset token
            PasswordResetToken.objects.create(
                user=user,
                token=token
            )
            
            # Send email
            send_password_reset_email(
                user_email=user.email,
                reset_token=token,
                user_name=user.get_full_name()
            )
            
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist
            pass
        
        return Response({
            'message': 'If an account exists with this email, a password reset link has been sent.'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token.
    POST /api/auth/password-reset-confirm/
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(description="Password reset successful"),
            400: OpenApiResponse(description="Bad Request - Invalid token or password")
        },
        tags=['Authentication'],
        description="Reset password using token received via email."
    )
    def post(self, request):
        """Confirm password reset with token."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['new_password']
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token.is_used = True
        reset_token.used_at = timezone.now()
        reset_token.save()
        
        # Send notification email
        send_password_changed_notification(
            user_email=user.email,
            user_name=user.get_full_name()
        )
        
        return Response({
            'message': 'Password has been reset successfully. You can now login with your new password.'
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    Change password for authenticated user.
    POST /api/auth/change-password/
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Bad Request - Validation errors")
        },
        tags=['Authentication'],
        description="Change password for authenticated user. Requires current password."
    )
    def post(self, request):
        """Change password for authenticated user."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        new_password = serializer.validated_data['new_password']
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Send notification email
        send_password_changed_notification(
            user_email=user.email,
            user_name=user.get_full_name()
        )
        
        return Response({
            'message': 'Password changed successfully.'
        }, status=status.HTTP_200_OK)
