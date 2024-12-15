from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, ProductImage, Review, 
    CustomUser, OtpToken, Variant, Colour, Storage
)

# --- Inline Admins ---
class ProductImageInline(admin.TabularInline):
    """Inline configuration for managing Product Images."""
    model = ProductImage
    extra = 1  # Number of empty forms to display by default
    fields = ('image',)  # Fields to display in the inline form
    readonly_fields = ('image',)  # Make the image field read-only if needed
    show_change_link = True  # Allow linking to the product image admin
    can_delete = True  # Allow deletion of images
    min_num = 1  # Ensure at least one image exists

    def has_delete_permission(self, request, obj=None):
        """Allow deletion of related product images."""
        return True
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product."""
    list_display = ('name', 'stock', 'price', 'brand', 'is_active', 'category', 'display_thumbnail', 'product_images')
    inlines = [ProductImageInline]  # Inline for managing related images

    @admin.display(description='Thumbnail')
    def display_thumbnail(self, obj):
        """Display a thumbnail for the product."""
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border: 1px solid #ddd;" />',
                obj.thumbnail.url
            )
        return "No Image"

    def product_images(self, obj):
        """Display all associated product images as small previews."""
        images = obj.images.all()  # 'images' is the related_name for ProductImage model
        image_html = ""
        for image in images:
            if image.image and hasattr(image.image, 'url'):
                image_html += format_html(
                    '<img src="{}" width="50" height="50" style="object-fit: cover; margin: 2px;" />',
                    image.image.url
                )
        return format_html(image_html) if image_html else "No Images"

    product_images.short_description = 'Product Images'



# --- Custom User Admin ---
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin configuration for CustomUser."""
    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_superuser_label')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'last_login')

    def is_superuser_label(self, obj):
        """Display a label indicating if the user is a superuser."""
        if obj.is_superuser:
            return format_html('<span style="color: red; font-weight: bold;">Superuser</span>')
        return "Regular User"
    is_superuser_label.short_description = 'User Type'



# --- Review Admin ---
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Reviews."""
    list_display = ['id', 'user', 'product', 'rating', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_filter = ['product', 'user', 'rating']

# --- Category Admin ---
admin.site.register(Category)

# --- Product Image Admin ---
admin.site.register(ProductImage)

# --- Other Models ---
admin.site.register(OtpToken)
admin.site.register(Variant)
admin.site.register(Colour)
admin.site.register(Storage)
