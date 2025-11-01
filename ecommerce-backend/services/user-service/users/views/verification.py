"""
Email verification views.
Handles email verification and resend verification email.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
import secrets

from ..models import User, EmailVerificationToken
from ..serializers import (
    EmailVerificationSerializer,
    ResendVerificationSerializer,
)
from ..utils import send_email_verification_email


class VerifyEmailView(APIView):
    """
    Verify user email with token.
    POST /api/auth/verify-email/
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=EmailVerificationSerializer,
        responses={
            200: OpenApiResponse(description="Email verified successfully"),
            400: OpenApiResponse(description="Bad Request - Invalid token or email")
        },
        tags=['Authentication'],
        description="Verify user email address using token sent via email."
    )
    def post(self, request):
        """Verify email with token."""
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        verification_token = serializer.validated_data['verification_token']
        
        # Mark user as verified
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        
        # Mark token as used
        verification_token.mark_as_used()
        
        return Response({
            'message': 'Email verified successfully. You can now login to your account.'
        }, status=status.HTTP_200_OK)


class ResendVerificationEmailView(APIView):
    """
    Resend verification email.
    POST /api/auth/resend-verification/
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=ResendVerificationSerializer,
        responses={
            200: OpenApiResponse(description="Verification email sent successfully"),
            400: OpenApiResponse(description="Bad Request - Email already verified or invalid")
        },
        tags=['Authentication'],
        description="Resend email verification token. Only works for unverified accounts."
    )
    def post(self, request):
        """Resend verification email."""
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Invalidate old tokens
            EmailVerificationToken.objects.filter(
                user=user,
                is_used=False
            ).update(is_used=True)
            
            # Generate new token
            token = secrets.token_urlsafe(32)
            
            # Create email verification token
            EmailVerificationToken.objects.create(
                user=user,
                token=token
            )
            
            # Send verification email
            send_email_verification_email(
                user_email=user.email,
                verification_token=token,
                user_name=user.get_full_name()
            )
            
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist
            pass
        
        return Response({
            'message': 'If an unverified account exists with this email, a verification link has been sent.'
        }, status=status.HTTP_200_OK)
