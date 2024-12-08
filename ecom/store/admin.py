from django.contrib import admin
from .models import Category, Product, ProductImage,  Review,CustomUser,OtpToken
from django.utils.html import format_html  # Import format_html (if needed)

# Inline admin for product images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Number of extra image upload fields

# Admin configuration for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category','thumbnail')  # Display fields
    search_fields = ('name', 'description')  # Add a search box for these fields
    list_filter = ('category', 'price')  # Filters on the right sidebar
    ordering = ('-price',)  # Default ordering by price (descending)
    inlines = [ProductImageInline]  # Inline images

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     # Customize the list display and add fields as needed
#     list_display = ('username', 'email', 'is_staff', 'is_active')
#     search_fields = ('username', 'email')
#     list_filter = ('is_staff', 'is_active')

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Customize the list display
    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_superuser_label')
    
    # Search fields for quick search
    search_fields = ('username', 'email')

    # Filters to categorize users by their attributes
    list_filter = ('is_staff', 'is_active', 'is_superuser','last_login')
    
    # Add a custom method to display if the user is a superuser
    def is_superuser_label(self, obj):
        # Check if the user is a superuser and display differently
        if obj.is_superuser:
            return format_html('<span style="color: red; font-weight: bold;">Superuser</span>')
        return "Regular User"

    is_superuser_label.short_description = 'User Type'  # Display name for the column

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=['id','user','product','rating','created_at']
    readonly_fields=['created_at']
    ordering=['-created_at']
    list_filter = ['product', 'user', 'rating']  # Add filters for product, user, and rating

# Register your models here
# admin.site.register(Product, ProductAdmin)  # Register Product with its custom admin
admin.site.register(Category)  # Register Category model
admin.site.register(ProductImage) 
admin.site.register(OtpToken)
 

from django.contrib import admin

@admin.action(description="Restock selected products")
def restock_products(modeladmin, request, queryset):
    for product in queryset:
        product.increase_stock(10)  # Increase stock by 10 as an example

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'stock', 'price', 'Brand', 'category', 'thumbnail')  # Include the custom 'thumbnail' method in list_display
#     actions = [restock_products]

#     def thumbnail(self, obj):
#         if obj.thumbnail:
#             return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.thumbnail.url)
#         return "No Image"
    
#     thumbnail.short_description = 'Thumbnail'

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage

# # Inline model for ProductImage
# class ProductImageInline(admin.TabularInline):  # Or admin.StackedInline for a different layout
#     model = ProductImage
#     extra = 1  # Number of empty forms to display by default
#     fields = ('image',)  # Only show the image field (you can add other fields if needed)
#     readonly_fields = ('image',)  # Makes the image field read-only if you want


 #Inline Admin for ProductImage
class ProductImageInline(admin.TabularInline):  # Use TabularInline or StackedInline
    model = ProductImage
    extra = 1  # Number of empty forms to display by default
    fields = ('image',)  # Fields to display in the inline form
    readonly_fields = ('image',)  # Make the image field read-only if you want
    show_change_link = True  # Allow linking to the product image admin
    can_delete = True  # Allow deletion of images
    min_num = 1  # Ensure at least one image exists

    def has_delete_permission(self, request, obj=None):
        return True  # Allow deletion of related product images


#product admin 
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'stock', 'price', 'Brand','is_active', 'category', 'display_thumbnail','product_images')  # Add custom thumbnail method
    # actions = [restock_products]
    inlines = [ProductImageInline]  # Optional: Add inline for product images if needed
  
    @admin.display(description='Thumbnail')  # Set the column name in admin
    def display_thumbnail(self, obj):
        if obj.thumbnail and obj.thumbnail.url:  # Check if thumbnail exists
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border: 1px solid #ddd;"/>', 
                obj.thumbnail.url
            )
        return "No Image"
    

    def product_images(self, obj):
        # Display all associated product images as small previews
        images = obj.images.all()  # 'images' is the related_name for ProductImage model
        image_html = ""
        for image in images:
            image_html += format_html('<img src="{}" width="50" height="50" style="object-fit: cover; margin: 2px;" />', image.image.url)
        return format_html(image_html) if image_html else "No Images"
    
    product_images.short_description = 'Product Images'  # Custom header for the column
 
 