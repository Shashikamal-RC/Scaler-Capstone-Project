"""
User profile views.
Handles current user profile display and updates.
"""
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from ..serializers import UserSerializer, UserUpdateSerializer


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
