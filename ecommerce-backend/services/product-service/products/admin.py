"""
Django Admin configuration for Product Service models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductVariant, ProductImage, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""
    list_display = ['name', 'slug', 'parent', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    list_editable = ['order', 'is_active']


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


class ProductVariantInline(admin.TabularInline):
    """Inline admin for product variants."""
    model = ProductVariant
    extra = 0
    fields = ['name', 'sku', 'price_adjustment', 'stock_quantity', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""
    list_display = [
        'name', 'sku', 'category', 'price', 'stock_quantity',
        'is_active', 'is_featured', 'average_rating', 'created_at'
    ]
    list_filter = ['is_active', 'is_featured', 'is_available', 'category', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['average_rating', 'review_count', 'view_count', 'created_at', 'updated_at']
    list_editable = ['is_active', 'is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'category', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_at_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'low_stock_threshold')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'is_available')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Measurements', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('average_rating', 'review_count', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Admin interface for ProductVariant model."""
    list_display = ['name', 'product', 'sku', 'price_adjustment', 'stock_quantity', 'is_active']
    list_filter = ['is_active', 'product__category']
    search_fields = ['name', 'sku', 'product__name']
    list_editable = ['is_active']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin interface for ProductImage model."""
    list_display = ['product', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['is_primary', 'order']
    
    def image_preview(self, obj):
        """Display image thumbnail in admin."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin interface for ProductReview model."""
    list_display = [
        'product', 'user_name', 'rating', 'is_approved',
        'is_verified_purchase', 'helpful_count', 'created_at'
    ]
    list_filter = ['is_approved', 'is_verified_purchase', 'rating', 'created_at']
    search_fields = ['product__name', 'user_name', 'user_email', 'title', 'comment']
    readonly_fields = [
        'user_id', 'user_email', 'user_name', 'helpful_count',
        'approved_by', 'approved_at', 'created_at', 'updated_at'
    ]
    list_editable = ['is_approved']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'rating', 'title', 'comment')
        }),
        ('User Information', {
            'fields': ('user_id', 'user_email', 'user_name', 'is_verified_purchase')
        }),
        ('Status', {
            'fields': ('is_approved', 'approved_by', 'approved_at', 'helpful_count')
        }),
        ('Admin Response', {
            'fields': ('admin_response', 'admin_response_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'unapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        """Bulk approve reviews."""
        count = 0
        for review in queryset:
            if not review.is_approved:
                review.approve(request.user.id)
                count += 1
        self.message_user(request, f'{count} review(s) approved.')
    approve_reviews.short_description = 'Approve selected reviews'
    
    def unapprove_reviews(self, request, queryset):
        """Bulk unapprove reviews."""
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} review(s) unapproved.')
    unapprove_reviews.short_description = 'Unapprove selected reviews'
