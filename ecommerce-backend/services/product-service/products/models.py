"""
Product Service Models.

Models for managing products, categories, variants, images, and reviews.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    """Abstract base model with common fields."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    """Product category model with hierarchical support."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    order = models.IntegerField(default=0, help_text="Display order")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_ancestors(self):
        """Get all parent categories."""
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.insert(0, parent)
            parent = parent.parent
        return ancestors

    def get_descendants(self):
        """Get all child categories recursively."""
        descendants = list(self.children.all())
        for child in self.children.all():
            descendants.extend(child.get_descendants())
        return descendants


class Product(BaseModel):
    """Main product model."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, help_text="Stock Keeping Unit")
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Original price for discount display"
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Cost price for profit calculation"
    )
    
    # Inventory
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    low_stock_threshold = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Alert when stock falls below this number"
    )
    
    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    
    # Measurements
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kg"
    )
    length = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Length in cm"
    )
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Width in cm"
    )
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Height in cm"
    )
    
    # Stats (denormalized for performance)
    view_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active', 'is_available']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_featured', '-created_at']),
            models.Index(fields=['average_rating']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        """Check if product is low on stock."""
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_at_price exists."""
        if self.compare_at_price and self.compare_at_price > self.price:
            return round(((self.compare_at_price - self.price) / self.compare_at_price) * 100, 2)
        return 0

    def update_rating(self):
        """Update average rating and review count from reviews."""
        reviews = self.reviews.filter(is_approved=True)
        self.review_count = reviews.count()
        if self.review_count > 0:
            self.average_rating = reviews.aggregate(
                avg=models.Avg('rating')
            )['avg']
        else:
            self.average_rating = 0
        self.save(update_fields=['average_rating', 'review_count', 'updated_at'])


class ProductVariant(BaseModel):
    """Product variants (e.g., different sizes, colors)."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    name = models.CharField(max_length=100, help_text="e.g., 'Red - Large'")
    sku = models.CharField(max_length=100, unique=True)
    
    # Variant attributes
    attributes = models.JSONField(
        default=dict,
        help_text="JSON object with variant attributes: {'color': 'Red', 'size': 'Large'}"
    )
    
    # Pricing (optional override of product price)
    price_adjustment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Price adjustment from base product price (can be negative)"
    )
    
    # Inventory
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Optional image for this variant
    image = models.ImageField(upload_to='variants/', null=True, blank=True)

    class Meta:
        ordering = ['product', 'name']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['sku']),
        ]
        unique_together = [['product', 'name']]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def final_price(self):
        """Calculate final price with adjustment."""
        return self.product.price + self.price_adjustment

    @property
    def is_in_stock(self):
        """Check if variant is in stock."""
        return self.stock_quantity > 0


class ProductImage(BaseModel):
    """Product images."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0, help_text="Display order")

    class Meta:
        ordering = ['-is_primary', 'order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
            models.Index(fields=['product', 'order']),
        ]

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        """Ensure only one primary image per product."""
        if self.is_primary:
            # Set all other images to non-primary
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductReview(BaseModel):
    """Product reviews and ratings."""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    # User reference (stored as UUID from User Service)
    user_id = models.UUIDField(help_text="User ID from User Service")
    user_email = models.EmailField(help_text="User email for display")
    user_name = models.CharField(max_length=255, help_text="User name for display")
    
    # Review content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=255)
    comment = models.TextField()
    
    # Status
    is_approved = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)
    
    # Admin moderation
    approved_by = models.UUIDField(null=True, blank=True, help_text="Admin user ID who approved")
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Helpful votes
    helpful_count = models.IntegerField(default=0)
    
    # Admin response
    admin_response = models.TextField(blank=True)
    admin_response_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['user_id']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['rating']),
        ]
        unique_together = [['product', 'user_id']]

    def __str__(self):
        return f"Review by {self.user_name} for {self.product.name}"

    def save(self, *args, **kwargs):
        """Update product rating when review is saved."""
        is_new = self._state.adding
        was_approved = False
        
        if not is_new:
            try:
                old = ProductReview.objects.get(pk=self.pk)
                was_approved = old.is_approved
            except ProductReview.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Update product rating if approval status changed
        if is_new or (self.is_approved != was_approved):
            self.product.update_rating()

    def delete(self, *args, **kwargs):
        """Update product rating when review is deleted."""
        product = self.product
        super().delete(*args, **kwargs)
        product.update_rating()

    def approve(self, admin_user_id):
        """Approve the review."""
        self.is_approved = True
        self.approved_by = admin_user_id
        self.approved_at = timezone.now()
        self.save()
