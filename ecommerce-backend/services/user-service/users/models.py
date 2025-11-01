import uuid
import secrets
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import EmailValidator, RegexValidator


# ==============================================================================
# USER MANAGER
# ==============================================================================

class UserManager(BaseUserManager):
    """
    Custom user manager for User model with email as unique identifier.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with admin privileges."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


# ==============================================================================
# USER MODEL
# ==============================================================================

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email as the unique identifier.
    Stores user account information and authentication details.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique user identifier"
    )
    
    email = models.EmailField(
        max_length=255,
        unique=True,
        validators=[EmailValidator()],
        help_text="User email address (used for login)"
    )
    
    first_name = models.CharField(
        max_length=100,
        help_text="User's first name"
    )
    
    last_name = models.CharField(
        max_length=100,
        help_text="User's last name"
    )
    
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        help_text="Contact phone number"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user account is active"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether user has verified their email"
    )
    
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether user can log into admin site"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Account creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    # Many-to-Many relationship with UserRole through UserRoleMapping
    roles = models.ManyToManyField(
        'UserRole',
        through='UserRoleMapping',
        related_name='users',
        help_text="User roles"
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.get_full_name()}"
    
    def get_full_name(self):
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return user's first name."""
        return self.first_name
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.roles.filter(name=role_name).exists()


# ==============================================================================
# USER ROLE MODEL
# ==============================================================================

class UserRole(models.Model):
    """
    Defines user roles (CUSTOMER, ADMIN, MANAGER).
    """
    
    class RoleChoices(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        ADMIN = 'ADMIN', 'Administrator'
        MANAGER = 'MANAGER', 'Manager'
    
    id = models.AutoField(primary_key=True)
    
    name = models.CharField(
        max_length=50,
        unique=True,
        choices=RoleChoices.choices,
        help_text="Role name"
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Role description"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Role creation timestamp"
    )
    
    class Meta:
        db_table = 'user_roles'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.get_name_display()}"


# ==============================================================================
# USER ROLE MAPPING MODEL
# ==============================================================================

class UserRoleMapping(models.Model):
    """
    Maps users to roles (Many-to-Many through table).
    """
    
    id = models.AutoField(primary_key=True)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='role_mappings',
        help_text="User"
    )
    
    role = models.ForeignKey(
        UserRole,
        on_delete=models.CASCADE,
        related_name='user_mappings',
        help_text="Role"
    )
    
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Role assignment timestamp"
    )
    
    class Meta:
        db_table = 'user_role_mapping'
        verbose_name = 'User Role Mapping'
        verbose_name_plural = 'User Role Mappings'
        unique_together = [['user', 'role']]  # Prevent duplicate assignments
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
            models.Index(fields=['assigned_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


# ==============================================================================
# USER ADDRESS MODEL
# ==============================================================================

class UserAddress(models.Model):
    """
    Stores user delivery and billing addresses.
    """
    
    class AddressType(models.TextChoices):
        SHIPPING = 'SHIPPING', 'Shipping Address'
        BILLING = 'BILLING', 'Billing Address'
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique address identifier"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        help_text="User who owns this address"
    )
    
    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        help_text="Address type (shipping or billing)"
    )
    
    full_name = models.CharField(
        max_length=200,
        help_text="Recipient's full name"
    )
    
    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        help_text="Contact phone number"
    )
    
    address_line1 = models.CharField(
        max_length=255,
        help_text="Street address, P.O. box"
    )
    
    address_line2 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Apartment, suite, unit, building, floor, etc."
    )
    
    city = models.CharField(
        max_length=100,
        help_text="City"
    )
    
    state = models.CharField(
        max_length=100,
        help_text="State/Province/Region"
    )
    
    postal_code = models.CharField(
        max_length=20,
        help_text="ZIP/Postal code"
    )
    
    country = models.CharField(
        max_length=100,
        default='India',
        help_text="Country"
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text="Default address for this type"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Address creation timestamp"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    class Meta:
        db_table = 'user_addresses'
        verbose_name = 'User Address'
        verbose_name_plural = 'User Addresses'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['address_type']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.get_address_type_display()} ({self.city})"
    
    def get_full_address(self):
        """Return formatted full address."""
        address_parts = [
            self.address_line1,
            self.address_line2,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country
        ]
        return ", ".join(filter(None, address_parts))
    
    def save(self, *args, **kwargs):
        """Override save to ensure only one default address per type per user."""
        if self.is_default:
            # Set all other addresses of same type for this user to non-default
            UserAddress.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


# ==============================================================================
# PASSWORD RESET TOKEN MODEL
# ==============================================================================

class PasswordResetToken(models.Model):
    """
    Temporary tokens for password reset functionality.
    Tokens expire after 1 hour.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique token identifier"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        help_text="User requesting password reset"
    )
    
    token = models.CharField(
        max_length=255,
        unique=True,
        help_text="Reset token"
    )
    
    expires_at = models.DateTimeField(
        help_text="Token expiration timestamp"
    )
    
    is_used = models.BooleanField(
        default=False,
        help_text="Whether token has been used"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Token creation timestamp"
    )
    
    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Reset token for {self.user.email} - {'Used' if self.is_used else 'Active'}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate token and set expiration."""
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if token is valid (not expired and not used)."""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Mark token as used."""
        self.is_used = True
        self.save(update_fields=['is_used'])
    
    @classmethod
    def cleanup_expired(cls):
        """Delete expired tokens (call this periodically)."""
        expired_tokens = cls.objects.filter(expires_at__lt=timezone.now())
        count = expired_tokens.count()
        expired_tokens.delete()
        return count


# ==============================================================================
# EMAIL VERIFICATION TOKEN MODEL
# ==============================================================================

class EmailVerificationToken(models.Model):
    """
    Stores email verification tokens for new user registrations.
    Tokens are used to verify user email addresses.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_verification_tokens',
        help_text="User associated with this verification token"
    )
    
    token = models.CharField(
        max_length=64,
        unique=True,
        help_text="Unique verification token"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the token was created"
    )
    
    expires_at = models.DateTimeField(
        help_text="When the token expires"
    )
    
    is_used = models.BooleanField(
        default=False,
        help_text="Whether the token has been used"
    )
    
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the token was used"
    )
    
    class Meta:
        db_table = 'email_verification_tokens'
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Verification token for {self.user.email} - {'Used' if self.is_used else 'Active'}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate token and set expiration."""
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            # Email verification tokens expire in 24 hours
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if token is valid (not expired and not used)."""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Mark token as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
    
    @classmethod
    def cleanup_expired(cls):
        """Delete expired tokens (call this periodically)."""
        expired_tokens = cls.objects.filter(expires_at__lt=timezone.now())
        count = expired_tokens.count()
        expired_tokens.delete()
        return count
