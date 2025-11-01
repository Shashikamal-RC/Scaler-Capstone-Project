from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    TokenResponseSerializer,
    UserSerializer,
    UserUpdateSerializer,
    generate_tokens_for_user
)

User = get_user_model()


# ==============================================================================
# AUTHENTICATION VIEWS
# ==============================================================================

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
        description="Register a new user account. Automatically assigns CUSTOMER role and returns JWT tokens."
    )
    def post(self, request):
        """Register a new user."""
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create user
            user = serializer.save()
            
            # Generate tokens
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


# ==============================================================================
# USER PROFILE VIEWS
# ==============================================================================

class CurrentUserView(APIView):
    """
    API endpoint for current user profile.
    
    GET /api/users/me - Get current user profile
    PUT /api/users/me - Update current user profile
    PATCH /api/users/me - Partial update current user profile
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: UserSerializer},
        tags=['User Profile'],
        description="Get the authenticated user's profile information."
    )
    def get(self, request):
        """Get current user profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        tags=['User Profile'],
        description="Update the authenticated user's profile information."
    )
    def put(self, request):
        """Update current user profile (full update)."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=False
        )
        if serializer.is_valid():
            serializer.save()
            user_serializer = UserSerializer(request.user)
            return Response(user_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        tags=['User Profile'],
        description="Partially update the authenticated user's profile information."
    )
    def patch(self, request):
        """Update current user profile (partial update)."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            user_serializer = UserSerializer(request.user)
            return Response(user_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
