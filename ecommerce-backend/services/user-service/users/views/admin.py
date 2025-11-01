"""
Admin management views.
Handles user management, role assignment, and user status updates.
"""
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from django.shortcuts import get_object_or_404
from django.db import models

from ..models import User, UserRole
from ..serializers import (
    AdminUserListSerializer,
    AdminUserDetailSerializer,
    RoleAssignmentSerializer,
    UserStatusSerializer,
    AdminCreateUserSerializer,
)


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has ADMIN role
        return request.user.roles.filter(name='ADMIN').exists() or request.user.is_staff


class AdminUserPagination(PageNumberPagination):
    """Pagination for admin user list."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminUserListView(generics.ListCreateAPIView):
    """
    List all users or create new user (admin only).
    GET /api/admin/users/
    POST /api/admin/users/
    """
    permission_classes = [IsAdminUser]
    pagination_class = AdminUserPagination
    
    def get_queryset(self):
        """Get all users with optional filtering."""
        queryset = User.objects.all().prefetch_related('roles').order_by('-created_at')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by verified status
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(roles__name=role)
        
        # Search by email, name, or phone
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(phone_number__icontains=search)
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == 'POST':
            return AdminCreateUserSerializer
        return AdminUserListSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='is_active', type=bool, description='Filter by active status'),
            OpenApiParameter(name='is_verified', type=bool, description='Filter by verified status'),
            OpenApiParameter(name='role', type=str, description='Filter by role name'),
            OpenApiParameter(name='search', type=str, description='Search by email, name, or phone'),
        ],
        responses={200: AdminUserListSerializer(many=True)},
        tags=['Admin'],
        description="Get paginated list of all users with optional filters. Admin only."
    )
    def get(self, request, *args, **kwargs):
        """List all users."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        request=AdminCreateUserSerializer,
        responses={
            201: AdminUserDetailSerializer,
            400: OpenApiResponse(description="Bad Request - Validation errors")
        },
        tags=['Admin'],
        description="Create a new user with specified roles. Admin only."
    )
    def post(self, request, *args, **kwargs):
        """Create new user."""
        return super().create(request, *args, **kwargs)


class AdminUserDetailView(APIView):
    """
    Get, update, or delete specific user (admin only).
    GET/PUT/PATCH/DELETE /api/admin/users/{id}/
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        responses={200: AdminUserDetailSerializer},
        tags=['Admin'],
        description="Get detailed information about a specific user. Admin only."
    )
    def get(self, request, user_id):
        """Get user details."""
        user = get_object_or_404(User.objects.prefetch_related('roles'), id=user_id)
        serializer = AdminUserDetailSerializer(user)
        return Response(serializer.data)
    
    @extend_schema(
        request=AdminUserDetailSerializer,
        responses={200: AdminUserDetailSerializer},
        tags=['Admin'],
        description="Update user information. Admin only."
    )
    def patch(self, request, user_id):
        """Update user details."""
        user = get_object_or_404(User, id=user_id)
        serializer = AdminUserDetailSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @extend_schema(
        responses={204: OpenApiResponse(description="User deleted successfully")},
        tags=['Admin'],
        description="Delete a user. Admin only."
    )
    def delete(self, request, user_id):
        """Delete user."""
        user = get_object_or_404(User, id=user_id)
        
        # Prevent deleting yourself
        if user.id == request.user.id:
            return Response(
                {'error': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignRoleView(APIView):
    """
    Assign role to user.
    POST /api/admin/users/{id}/assign-role/
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        request=RoleAssignmentSerializer,
        responses={
            200: OpenApiResponse(description="Role assigned successfully"),
            400: OpenApiResponse(description="Bad Request")
        },
        tags=['Admin'],
        description="Assign a role to a user. Admin only."
    )
    def post(self, request, user_id):
        """Assign role to user."""
        user = get_object_or_404(User, id=user_id)
        serializer = RoleAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        role_name = serializer.validated_data['role_name']
        role = UserRole.objects.get(name=role_name)
        
        # Check if user already has this role
        if user.roles.filter(id=role.id).exists():
            return Response(
                {'message': f'User already has {role_name} role.'},
                status=status.HTTP_200_OK
            )
        
        user.roles.add(role)
        
        return Response({
            'message': f'{role_name} role assigned to {user.email} successfully.',
            'roles': [r.name for r in user.roles.all()]
        }, status=status.HTTP_200_OK)


class RemoveRoleView(APIView):
    """
    Remove role from user.
    DELETE /api/admin/users/{id}/remove-role/
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        request=RoleAssignmentSerializer,
        responses={
            200: OpenApiResponse(description="Role removed successfully"),
            400: OpenApiResponse(description="Bad Request")
        },
        tags=['Admin'],
        description="Remove a role from a user. Admin only."
    )
    def delete(self, request, user_id):
        """Remove role from user."""
        user = get_object_or_404(User, id=user_id)
        serializer = RoleAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        role_name = serializer.validated_data['role_name']
        role = UserRole.objects.get(name=role_name)
        
        # Check if user has this role
        if not user.roles.filter(id=role.id).exists():
            return Response(
                {'message': f'User does not have {role_name} role.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent removing last role
        if user.roles.count() == 1:
            return Response(
                {'error': 'Cannot remove the last role from user. User must have at least one role.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.roles.remove(role)
        
        return Response({
            'message': f'{role_name} role removed from {user.email} successfully.',
            'roles': [r.name for r in user.roles.all()]
        }, status=status.HTTP_200_OK)


class ActivateUserView(APIView):
    """
    Activate user account.
    PATCH /api/admin/users/{id}/activate/
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        responses={200: OpenApiResponse(description="User activated successfully")},
        tags=['Admin'],
        description="Activate a user account. Admin only."
    )
    def patch(self, request, user_id):
        """Activate user."""
        user = get_object_or_404(User, id=user_id)
        
        if user.is_active:
            return Response(
                {'message': 'User is already active.'},
                status=status.HTTP_200_OK
            )
        
        user.is_active = True
        user.save(update_fields=['is_active'])
        
        return Response({
            'message': f'User {user.email} has been activated successfully.'
        }, status=status.HTTP_200_OK)


class DeactivateUserView(APIView):
    """
    Deactivate user account.
    PATCH /api/admin/users/{id}/deactivate/
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        responses={200: OpenApiResponse(description="User deactivated successfully")},
        tags=['Admin'],
        description="Deactivate a user account. Admin only."
    )
    def patch(self, request, user_id):
        """Deactivate user."""
        user = get_object_or_404(User, id=user_id)
        
        # Prevent deactivating yourself
        if user.id == request.user.id:
            return Response(
                {'error': 'You cannot deactivate your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.is_active:
            return Response(
                {'message': 'User is already inactive.'},
                status=status.HTTP_200_OK
            )
        
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        return Response({
            'message': f'User {user.email} has been deactivated successfully.'
        }, status=status.HTTP_200_OK)
