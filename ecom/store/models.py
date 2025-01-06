from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg
from PIL import Image
import datetime
from django_resized import ResizedImageField 
from django.conf import settings
import secrets
from django.contrib.auth import get_user_model 
from django.core.validators import RegexValidator
from django_countries.fields import CountryField
from image_cropping import ImageCropField, ImageRatioField
from django.utils import timezone
from django.core.exceptions import ValidationError

# Category of products
class Category(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'




# Users
class CustomUser(AbstractUser):      
    # Add custom fields here  

    profile_photo = ImageCropField(upload_to='profile_photos/', null=True, blank=True)
  
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)
   
    verification_method = models.CharField(
        max_length=20,
        choices=[('OTP', 'OTP'), ('Google', 'Google'), ('Facebook', 'Facebook')],
        default='OTP'
    )
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    

    def _str__(self):
        return self.email


User = get_user_model() # get the active user detils  

class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='addresses')
    address_line_1=models.CharField(max_length=255)
    address_line_2=models.CharField(max_length=255,blank=True)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    postal_code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(r'^[0-9A-Za-z]+$', 'Enter a valid postal code.')
        ]
    )
    country = models.CharField(max_length=100)



    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.country}"
    

    

class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6, default=secrets.token_hex(3))
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    
    
    def __str__(self):
        return self.user.username


# Colour Model
class Colour(models.Model):
    colour = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)  # For soft delete functionality
    is_deleted = models.BooleanField(default=False)  # Soft delete flag



    def __str__(self):
        return self.colour

# Storage Model
class Storage(models.Model):
    capacity = models.PositiveIntegerField()  # Use `PositiveIntegerField` for RAM/Storage
    is_active = models.BooleanField(default=True)  # For soft delete functionality
    is_deleted = models.BooleanField(default=False)  # Soft delete flag


    def __str__(self):
        return f"{self.capacity} GB"

#Products
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    brand = models.CharField(max_length=50,default='')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1,related_name="products")
    description = models.TextField(default='', blank=True, null=True)
    thumbnail = ResizedImageField(upload_to='uploads/product/',size=[300, 250], default='uploads/product/lap.jpg',crop=['middle', 'center'], force_format='JPEG')
    stock = models.PositiveIntegerField(default=0)  # For product stock
    is_active = models.BooleanField(default=True)  # For soft delete functionality
    is_deleted = models.BooleanField(default=False)  # Soft delete flag
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    is_featured = models.BooleanField(default=False)  # Featured flag
    discount = models.DecimalField(default=0, decimal_places=2, max_digits=10)  # Discount amount or percentage


   
    
    def __str__(self):
        return self.name

    def discounted_price(self):
        """Returns the price after applying the discount percentage."""
        if self.discount> 0:
            return self.price - (self.price * (self.discount / 100))
        return self.price

# Product Images
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = ResizedImageField(upload_to='uploads/product_images/',  size=[300, 250],crop=['middle', 'center'], force_format='JPEG')

    
    def __str__(self):
        return f"Image for {self.product.name}"
 

# Product Variants (Color and Storage)
class Variant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    colour = models.ForeignKey(Colour, on_delete=models.CASCADE,default=1)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE,default=1)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    stock = models.PositiveIntegerField(default=0)  # Stock for this specific variant
    is_active = models.BooleanField(default=True) 
    is_deleted = models.BooleanField(default=False)  # Soft delete flag

    def __str__(self):
        return f"{self.product.name} - {self.colour.colour}, {self.storage.capacity}GB"

 
#Review
class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    comment = models.TextField(blank=True)  # Detailed review text
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the review is created
    is_active = models.BooleanField(default=True)  # For soft delete functionality
    is_deleted = models.BooleanField(default=False)  # Soft delete flag


    def __str__(self):
        return f"Review by {self.user.first_name} for {self.product.name}"



class Cart(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='cart_items')
    variant=models.ForeignKey(Variant,on_delete=models.CASCADE,related_name='cart_items')
    quantity=models.PositiveBigIntegerField(default=1)
    added_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.variant} (Qty: {self.quantity})"

    def total_price(self):
        return self.variant.price * self.quantity


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=1)
    usage_count = models.PositiveIntegerField(default=0)

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("Start date must be earlier than the end date.")
        if not (0 < self.discount_percent <= 100):
            raise ValidationError("Discount percent must be between 0 and 100.")

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.usage_count < self.usage_limit

    def __str__(self):
        return f"{self.code} - {self.discount_percent}%"
    


class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    assigned_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.coupon.code} - {'Used' if self.is_used else 'Not Used'}"



from django.db import models
from django.conf import settings
 
    
class Wallet(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def add_funds(self, amount):
        self.balance += amount
        self.save()

    def deduct_funds(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.email}'s Wallet - Balance: ₹{self.balance}"
    

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('Refund', 'Refund'),
        ('Purchase', 'Purchase'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet_transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.amount}"

#orders
class Order(models.Model):
    STATUS_CHOICES=[
        ('Processing','Processing'),
        ('Shipped','Shipped'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled'),
        ('Returned', 'Returned')
    ]


    PAYMENT_CHOICES=[
        ('COD','Cash on Delivery'),
        ('Online','Online Payment')
    ]

    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='orders')
    address=models.ForeignKey(Address,on_delete=models.SET_NULL,null=True,blank=True,related_name='address_orders')
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='Processing')
    payment_method=models.CharField(max_length=10,choices=PAYMENT_CHOICES,default='COD')
    applied_coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True) 
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    wallet_amount_used = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    #online payement
    
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    payment_status = models.CharField(max_length=20, default='Pending', choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed')
    ])


    def __str__(self):
        return f"Orders #{self.id} by {self.user.email} - {self.status}"
    
    def cancel_order(self):
        if self.status not in['Cancelled','Delivered']:
            self.status='Cancelled'
            self.save()
            self.user.wallet.add_funds(self.total_price)
            WalletTransaction.objects.create( user=self.user, 
                    amount=self.total_price, 
                    transaction_type='Refund', 
                    description=f"Refund for cancelled order {self.id}" )
        else:
            raise ValueError('Order cannot be cancelled')


    def return_order(self): 
        if self.status == 'Delivered':
            self.status = 'Returned' # Change this to 'Returned'
            self.save()
            self.user.wallet.add_funds(self.total_price) 
            WalletTransaction.objects.create( 
                user=self.user, 
                amount=self.total_price,
                transaction_type='Refund', 
                description=f"Refund for returned order {self.id}" ) 
            
             
             
        else: 
            raise ValueError("Only delivered orders can be returned")
    


class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    variant=models.ForeignKey(Variant,on_delete=models.CASCADE,related_name='order_items')
    quantity=models.PositiveIntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.variant.product.name} {self.variant.colour.colour} {self.variant.storage.capacity}GB-Qty:{self.quantity}"
    
    def total_cost(self):
        return self.price*self.quantity




class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


 

 