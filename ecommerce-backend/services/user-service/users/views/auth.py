"""
Authentication views.
Handles user registration, login, logout, and token refresh.
"""
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
import secrets

from ..serializers import (
    RegisterSerializer,
    LoginSerializer,
    TokenResponseSerializer,
    generate_tokens_for_user,
)
from ..models import EmailVerificationToken
from ..utils import send_email_verification_email


class RegisterView(APIView):
    """
    API endpoint for user registration.
    
    POST /api/auth/register
    - Create new user account with CUSTOMER role
    - Returns JWT tokens and user data
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: TokenResponseSerializer,
            400: OpenApiResponse(description="Bad Request - Validation errors")
        },
        tags=['Authentication'],
        description="Register a new user account. Automatically assigns CUSTOMER role, sends verification email, and returns JWT tokens."
    )
    def post(self, request):
        """Register a new user."""
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create user
            user = serializer.save()
            
            # Generate verification token and send email
            token = secrets.token_urlsafe(32)
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
            
            # Generate JWT tokens
            token_data = generate_tokens_for_user(user)
            
            return Response(
                token_data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """
    API endpoint for user login.
    
    POST /api/auth/login
    - Authenticate user with email and password
    - Returns JWT tokens and user data
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request=LoginSerializer,
        responses={
            200: TokenResponseSerializer,
            400: OpenApiResponse(description="Bad Request - Invalid credentials")
        },
        tags=['Authentication'],
        description="Login with email and password. Returns JWT access and refresh tokens."
    )
    def post(self, request):
        """Login user and return tokens."""
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate tokens
            token_data = generate_tokens_for_user(user)
            
            return Response(
                token_data,
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    """
    API endpoint for user logout.
    
    POST /api/auth/logout
    - Blacklist the refresh token to prevent reuse
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'refresh': {'type': 'string', 'description': 'Refresh token to blacklist'}
                },
                'required': ['refresh']
            }
        },
        responses={
            205: OpenApiResponse(description="Reset Content - Logout successful"),
            400: OpenApiResponse(description="Bad Request - Invalid token")
        },
        tags=['Authentication'],
        description="Logout by blacklisting the refresh token."
    )
    def post(self, request):
        """Logout user by blacklisting refresh token."""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
