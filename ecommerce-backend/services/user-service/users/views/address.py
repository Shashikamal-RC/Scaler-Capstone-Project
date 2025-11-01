"""
Address management views.
Handles CRUD operations for user addresses.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from ..models import UserAddress
from ..serializers import UserAddressSerializer, UserAddressCreateSerializer


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners to access their addresses.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class UserAddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user addresses.
    
    Provides CRUD operations and custom actions:
    - list: GET /api/users/me/addresses/
    - create: POST /api/users/me/addresses/
    - retrieve: GET /api/users/me/addresses/{id}/
    - update: PUT /api/users/me/addresses/{id}/
    - partial_update: PATCH /api/users/me/addresses/{id}/
    - destroy: DELETE /api/users/me/addresses/{id}/
    - set_default: PATCH /api/users/me/addresses/{id}/set-default/
    """
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """Return addresses for the authenticated user only."""
        return UserAddress.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use different serializers for read and write operations."""
        if self.action in ['create', 'update', 'partial_update']:
            return UserAddressCreateSerializer
        return UserAddressSerializer
    
    @extend_schema(
        responses={200: UserAddressSerializer(many=True)},
        tags=['User Addresses'],
        description="Get all addresses for the authenticated user."
    )
    def list(self, request, *args, **kwargs):
        """List all addresses for the current user."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        request=UserAddressCreateSerializer,
        responses={
            201: UserAddressSerializer,
            400: OpenApiResponse(description="Bad Request - Validation errors")
        },
        tags=['User Addresses'],
        description="Create a new address for the authenticated user."
    )
    def create(self, request, *args, **kwargs):
        """Create a new address."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = serializer.save()
        
        # Return full address details
        output_serializer = UserAddressSerializer(address)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        responses={200: UserAddressSerializer},
        tags=['User Addresses'],
        description="Get details of a specific address."
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific address."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        request=UserAddressCreateSerializer,
        responses={200: UserAddressSerializer},
        tags=['User Addresses'],
        description="Update an address (full update)."
    )
    def update(self, request, *args, **kwargs):
        """Full update of an address."""
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        request=UserAddressCreateSerializer,
        responses={200: UserAddressSerializer},
        tags=['User Addresses'],
        description="Partially update an address."
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update of an address."""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        responses={204: OpenApiResponse(description="Address deleted successfully")},
        tags=['User Addresses'],
        description="Delete an address. If the deleted address was default, automatically sets another address of the same type as default."
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete an address.
        If the deleted address was default, automatically set another address 
        of the same type as default.
        """
        address = self.get_object()
        was_default = address.is_default
        address_type = address.address_type
        
        # Delete the address
        response = super().destroy(request, *args, **kwargs)
        
        # If deleted address was default, set another one as default
        if was_default:
            next_address = UserAddress.objects.filter(
                user=request.user,
                address_type=address_type
            ).first()
            
            if next_address:
                next_address.is_default = True
                next_address.save()
        
        return response
    
    @extend_schema(
        request=None,
        responses={
            200: UserAddressSerializer,
            400: OpenApiResponse(description="Bad Request")
        },
        tags=['User Addresses'],
        description="Set this address as the default for its type (shipping or billing)."
    )
    @action(detail=True, methods=['patch'], url_path='set-default')
    def set_default(self, request, pk=None):
        """
        Set an address as default for its type.
        Automatically unsets other default addresses of the same type.
        """
        address = self.get_object()
        
        # Set as default (model's save method handles unsetting others)
        address.is_default = True
        address.save()
        
        serializer = UserAddressSerializer(address)
        return Response(serializer.data)
