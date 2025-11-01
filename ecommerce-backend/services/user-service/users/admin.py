from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserRole, UserRoleMapping, UserAddress, PasswordResetToken


# ==============================================================================
# USER ADMIN
# ==============================================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    
    list_display = [
        'email', 'get_full_name', 'phone_number', 
        'is_active', 'is_verified', 'is_staff', 'created_at'
    ]
    list_filter = ['is_active', 'is_verified', 'is_staff', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('id', 'email', 'first_name', 'last_name', 'phone_number')
        }),
        ('Password', {
            'fields': ('password',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'phone_number',
                'password1', 'password2', 'is_active', 'is_verified', 'is_staff'
            )
        }),
    )
    
    def get_full_name(self, obj):
        """Display full name."""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


# ==============================================================================
# USER ROLE ADMIN
# ==============================================================================

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin for UserRole model."""
    
    list_display = ['name', 'description', 'user_count', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Role Information', {
            'fields': ('name', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def user_count(self, obj):
        """Display count of users with this role."""
        count = obj.users.count()
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            count
        )
    user_count.short_description = 'Users'


# ==============================================================================
# USER ROLE MAPPING ADMIN
# ==============================================================================

@admin.register(UserRoleMapping)
class UserRoleMappingAdmin(admin.ModelAdmin):
    """Admin for UserRoleMapping model."""
    
    list_display = ['user', 'role', 'assigned_at']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-assigned_at']
    readonly_fields = ['assigned_at']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Role Assignment', {
            'fields': ('user', 'role')
        }),
        ('Metadata', {
            'fields': ('assigned_at',)
        }),
    )


# ==============================================================================
# USER ADDRESS ADMIN
# ==============================================================================

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    """Admin for UserAddress model."""
    
    list_display = [
        'full_name', 'user', 'address_type', 'city', 
        'state', 'country', 'is_default', 'created_at'
    ]
    list_filter = ['address_type', 'country', 'is_default', 'created_at']
    search_fields = [
        'user__email', 'full_name', 'phone_number', 
        'city', 'state', 'postal_code'
    ]
    ordering = ['-is_default', '-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('User', {
            'fields': ('id', 'user', 'address_type', 'is_default')
        }),
        ('Contact Information', {
            'fields': ('full_name', 'phone_number')
        }),
        ('Address Details', {
            'fields': (
                'address_line1', 'address_line2', 
                'city', 'state', 'postal_code', 'country'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user')


# ==============================================================================
# PASSWORD RESET TOKEN ADMIN
# ==============================================================================

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin for PasswordResetToken model."""
    
    list_display = [
        'user', 'token_preview', 'is_used', 
        'is_expired', 'expires_at', 'created_at'
    ]
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'token']
    ordering = ['-created_at']
    readonly_fields = ['id', 'token', 'expires_at', 'created_at']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Token Information', {
            'fields': ('id', 'user', 'token')
        }),
        ('Status', {
            'fields': ('is_used', 'expires_at')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def token_preview(self, obj):
        """Display shortened token."""
        return f"{obj.token[:20]}..." if len(obj.token) > 20 else obj.token
    token_preview.short_description = 'Token'
    
    def is_expired(self, obj):
        """Display if token is expired."""
        from django.utils import timezone
        expired = timezone.now() > obj.expires_at
        color = 'red' if expired else 'green'
        status = 'Expired' if expired else 'Active'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    is_expired.short_description = 'Status'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user')
    
    actions = ['cleanup_expired_tokens']
    
    def cleanup_expired_tokens(self, request, queryset):
        """Admin action to cleanup expired tokens."""
        count = PasswordResetToken.cleanup_expired()
        self.message_user(
            request,
            f"Successfully deleted {count} expired token(s)."
        )
    cleanup_expired_tokens.short_description = "Delete expired tokens"
