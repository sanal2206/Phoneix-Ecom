from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from .models import Product,Category,ProductImage,CustomUser,OtpToken,Address,Cart,Variant,Wishlist,Wallet,Coupon,UserCoupon
from django.db.models import Avg
from django.contrib.auth import get_user_model
from django .contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm,ReviewForm,AddressForm,UserProfileForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail

# Create your views here.

 

@login_required
def home(request):
    # Get the filter and sorting values from the GET request
    search_query = request.GET.get('q', '')
    show_out_of_stock = request.GET.get('show_out_of_stock', 'no')
    sort_by = request.GET.get('sort_by', 'name_asc')

    # Start with the basic query, filtering only active and non-deleted products
    products = Product.objects.filter(is_active=True, is_deleted=False)

    # Filter by search query if provided
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Filter by stock availability
    if show_out_of_stock == 'no':
        products = products.filter(stock__gt=0)  # Assuming 'stock' is the field for product quantity

    # Sort products based on selected option
    if sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')
    elif sort_by == 'price_low_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_low':
        products = products.order_by('-price')
    elif sort_by == 'new_arrivals':
        products = products.order_by('-created_at')  # Assuming 'created_at' is the date of creation
    elif sort_by == 'featured':
        products = products.filter(is_featured=True)  # Assuming 'is_featured' is a boolean field for featured products

    # Calculate the average rating for each product
    for product in products:
        avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']
        product.avg_rating = round(avg_rating, 1) if avg_rating else 0
        product.stars_range = range(1, 6)  # Create a range from 1 to 5 for stars

  
    # Fetch available coupons 
    available_coupons = Coupon.objects.prefetch_related('usercoupon_set').filter( 
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(), 
        usercoupon__is_used=False,
        usercoupon__user=request.user
    ).distinct()
         
        

    return render(request, 'home.html', {
        'products': products,
        'search_query': search_query,
        'show_out_of_stock': show_out_of_stock,
        'sort_by': sort_by,
        'available_coupons': available_coupons,
    })



def about(request):
    return render(request,'about.html',{})


 

def login_user(request):
    if request.user.is_authenticated:
        return redirect("home") 
    
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:    
            login(request, user)
            messages.success(request, f"Hi {request.user.username}, you are now logged-in")
            return redirect("home")
        
        else:
            messages.warning(request, "Invalid credentials")
            return redirect("login")
        
    return render(request, "login.html")

def logout_user(request):
    logout(request)
    messages.success(request,('You have been logged out...Thanks for shopping'))
    return redirect('home')


#register

def register_user(request):
    
    
    form=SignUpForm()
    if request.method=='POST':
        form=SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Account created successfully,An OTP sent to your email')
            return redirect('verify-email',username=request.POST['username'])
    context={'form':form}
    return render(request,'register.html',context) 
 

 

def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()
    
    try:
            
        if request.method == 'POST':
            # valid token
            if user_otp.otp_code == request.POST['otp_code']:
                
                # checking for expired token
                if user_otp.otp_expires_at > timezone.now():
                    user.is_active=True
                    user.save()
                    messages.success(request, "Account activated successfully!! You can Login.")
                    return redirect("login")
                
                # expired token
                else:
                    messages.warning(request, "The OTP has expired, get a new OTP!")
                    return redirect("verify-email", username=user.username)
            
            
            # invalid otp code
            else:
                messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
                return redirect("verify-email", username=user.username)
            
        context = {}
        return render(request, "verify_token.html", context)
    except:
        return render(request,'verify-email')




def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]
        
        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
            
            
            # email variables
            subject="Email Verification"
            message = f"""
                                Hi {user.username}, here is your OTP {otp.otp_code} 
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/verify-email/{user.username}
                                
                                """
            sender = "sanalsabu22@gmail.com"
            receiver = [user.email, ]
        
        
            # send email
            send_mail(
                    subject,
                    message,
                    sender,
                    receiver,
                    fail_silently=False,
                )
            
            messages.success(request, "A new OTP has been sent to your email-address")
            return redirect("verify-email", username=user.username)

        else:
            messages.warning(request, "This email dosen't exist in the database")
            return redirect("resend-otp")
        
           
    context = {}
    return render(request, "resend_otp.html", context)
from django.db.models import Q


@login_required
def product(request, pk):
    # Get the product by primary key (id)
    products = get_object_or_404(Product, id=pk, is_active=True, is_deleted=False)
    
    # Fetch images for the product
    images = ProductImage.objects.filter(product=products)
    
    # Fetch active variants for the product
    variants = products.variants.filter(is_active=True)
   
    
    
    # Get related products (same category but excluding the current product)
    related_products = Product.objects.filter(category=products.category, is_active=True).exclude(pk=pk)[:4]  # Show up to 4 related products
    
    # Calculate the average rating for the product
    avg_rating = products.reviews.aggregate(Avg('rating'))['rating__avg']  # Get the average rating
    avg_rating = round(avg_rating, 1) if avg_rating else 0  # Round to 1 decimal place, default to 0 if no reviews
    
    # Fetch reviews for the product
    reviews = products.reviews.all()  # Access the reviews related to the product
    
    # Initialize the review form
    form = ReviewForm()

    # Handle POST request for adding a review
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
             
            has_ordered = OrderItem.objects.filter(
                Q(order__user=request.user) & Q(variant__product=products)
            ).exists()


            if not has_ordered:
                messages.error(request,"You can only review products you have purchased.")
                return redirect('product', pk=products.id)

            review = form.save(commit=False)
            review.product = products  # Associate the review with the current product
            review.user = request.user  # Associate the review with the logged-in user
            review.save()  # Save the review to the database
            messages.success(request, "Your review has been submitted successfully!")

            return redirect('product', pk=products.id)  # Redirect to the same product page after saving the review

    context = {
        'products': products,
        'images': images,
        'related_products': related_products,
        'reviews': reviews,
        'form': form,  # Include the form for adding reviews
        'avg_rating': avg_rating,  # Pass the average rating to the template
        'variants': variants  # Include the product variants
    }

    return render(request, 'product.html', context)


def category(request, cat):
  

    # Replace hyphens with spaces (if needed for consistency)
    cat = cat.replace('-', ' ')
    
    try:
        # Look up the category
        category = get_object_or_404(Category, name=cat,)  # This will raise a 404 if not found
        # Debugging statement
        
        # Get products in the category
        products = Product.objects.filter(category=category,is_active=True)
        
        for product in products:
            avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']
            product.avg_rating = round(avg_rating, 1) if avg_rating else 0
            product.stars_range = range(1, 6)  # Create a range from 1 to 5 for stars
        
        return render(request, 'category.html', {'products': products, 'category': category})
    
    except Category.DoesNotExist:
        # Specific exception if category not found
        print(f"Category not found: {cat}")  # Debugging statement
        messages.error(request, "Sorry... That category doesn't exist.")  # Use 'error' for better visibility
        return redirect('home')
    
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def user_profile(request):
    user = request.user
    
    # Get or create the wallet for the logged-in user
    wallet, created = Wallet.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'profile.html', {'form': form, 'wallet': wallet})


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('user_profile')  # Redirect to profile page after adding address
    else:
        form = AddressForm()
    return render(request, 'manage_address.html', {'form': form})


@login_required
def delete_address(request, address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    address.delete()
    return redirect('user_profile')  # Redirect to profile page after deleting address    


@login_required
def update_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        profile_photo = request.FILES.get('profile_photo')  # Get the uploaded image

        
        # Update the logged-in user's profile
        user = request.user
        user.username = username
        user.phone_number = phone_number  # Ensure your user model includes this field
        if profile_photo:
            user.profile_photo = profile_photo
        
        user.save()

        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    
    return render(request, 'profile.html', {'user': request.user})


@login_required
def manage_address_profile(request, address_id=None):
    # Retrieve the address instance if address_id is provided; otherwise, create a new form instance
    if address_id:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        form = AddressForm(instance=address)  # Pre-fill the form with existing address data
    else:
        address = None
        form = AddressForm()  # Empty form for creating a new address

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)  # Bind the form with POST data
        if form.is_valid():
            form.save()  # Save the address (either update or create)
            messages.success(request, "Address updated successfully!" if address else "Address added successfully!")
            return redirect('user_profile')  # Adjust the redirect URL as per your application

    context = {'form': form, 'address': address}
    return render(request, 'manage_address_profile.html', context)


#cart
@login_required
def add_to_cart(request, product_id, variant_id):
    product = get_object_or_404(Product, id=product_id)
    variant = get_object_or_404(Variant, id=variant_id)

    # Get the quantity from the form
    quantity = int(request.POST.get('quantity', 1))

    # Check if the requested quantity exceeds available stock
    if quantity > variant.stock:
        messages.error(request, f"Sorry, we only have {variant.stock} units of this variant in stock.")
        return redirect('product', pk=product.id)  # Redirect back to product page

    # Limit the maximum quantity per user (e.g., 5 per product/variant)
    max_quantity = 5

    # Retrieve the cart item for the user and variant, if it exists
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        variant=variant,
        defaults={'quantity': 0}  # Default quantity is 0 for new items
    )

    # Calculate the total quantity if the current quantity is added
    total_quantity = cart_item.quantity + quantity

    # Ensure the total quantity does not exceed the maximum allowed limit
    if total_quantity > max_quantity:
        allowed_quantity = max_quantity - cart_item.quantity
        messages.error(
            request,
            f"You can only add {allowed_quantity} more units of this product to your cart. "
            f"The maximum allowed is {max_quantity}."
        )
        return redirect('product', pk=product.id)

    # Ensure the total quantity does not exceed the stock
    if total_quantity > variant.stock:
        allowed_stock = variant.stock - cart_item.quantity
        messages.error(
            request,
            f"Sorry, you can only add {allowed_stock} more units of this variant. "
            f"We have {variant.stock} units in stock."
        )
        return redirect('product', pk=product.id)

    # Update the cart item quantity or create a new entry
    cart_item.quantity = total_quantity
    cart_item.save()

    # Success message
    messages.success(request, "Item added to your cart successfully!")
    return redirect('view_cart')  # Redirect to the cart page



from decimal import Decimal

def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    # Calculate subtotal (price without discount) and discount total
    subtotal = sum(Decimal(item.variant.price) * item.quantity for item in cart_items)
    discount_total = sum(
        (Decimal(item.variant.price) * (Decimal(item.variant.product.discount) / 100)) * item.quantity
        for item in cart_items if item.variant.product.discount > 0
    )

    # Convert shipping cost to Decimal
    shipping_cost = Decimal('5.00')

    # Calculate final total (subtotal - discount + shipping)
    total = subtotal - discount_total + shipping_cost

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_total': discount_total,
        'total': total,
    })



def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from your cart.")
    return redirect('view_cart')




def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))

        if quantity > cart_item.variant.stock:
            messages.error(request, f"Only {cart_item.variant.stock} units available in stock.")
        elif quantity>5:
                messages.error(request, "Your are allowed to add  max 5 items to the cart.")

        elif quantity < 1:
            messages.error(request, "Quantity must be at least 1.")
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully.")

    return redirect('view_cart')


 


# #check_out view
# @login_required
# def checkout(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     if not cart_items.exists():
#         messages.error(request, "Your cart is empty. Please add items before checkout.")
#         return redirect('cart')
    
#     # Reuse calculations from view_cart
#     subtotal = sum(Decimal(item.variant.price) * item.quantity for item in cart_items)
#     discount_total = sum(
#         (Decimal(item.variant.price) * (Decimal(item.variant.product.discount) / 100)) * item.quantity
#         for item in cart_items if item.variant.product.discount > 0
#     )


#     coupon_discount = Decimal('0.00')
#     applied_coupon = None 
#     coupon_id = request.session.get('applied_coupon_id') 
#     if coupon_id:
#         try: 
#             user_coupon = UserCoupon.objects.get( user=request.user, coupon_id=coupon_id, is_used=False, )
#             coupon =user_coupon.coupon

#             #verfiy coupon is still valid
#             current_time=now()
#             if(coupon.start_date<=current_time<=coupon.end_date and coupon.usage_count< coupon.usage_limit and coupon.is_active):

#                 applied_coupon=coupon
#                 # Calculate coupon discount on remaining amount after product discounts
#                 discountable_amount=subtotal-discount_total
#                 coupon_discount = (discountable_amount * Decimal(coupon.discount_percent) / 100)
#             else:
#                 #Remove invalid coupon from session
#                 request.session.pop('applied_coupon_id', None) 
#                 messages.error(request, "Coupon is no longer valid.")
#         except UserCoupon.DoesNotExist:
#             request.session.pop('applied_coupon_id', None)                  
    
#     shipping_cost = Decimal('5.00')
     
#     total = subtotal - discount_total - coupon_discount + shipping_cost
    

#     addresses = Address.objects.filter(user=request.user)

#     if request.method == 'POST':
#         selected_address_id = request.POST.get('address_id')
#         if selected_address_id:
#             address = get_object_or_404(Address, id=selected_address_id, user=request.user)
#             return redirect('place_order_from_cart', address_id=address.id)
#         else:
#             address_form = AddressForm(request.POST)
#             if address_form.is_valid():
#                 address = address_form.save(commit=False)
#                 address.user = request.user
#                 address.save()
#                 return redirect('place_order_from_cart', address_id=address.id)

#     return render(request, 'checkout.html', {
#         'cart_items': cart_items,
#         'addresses': addresses,
#         'address_form': AddressForm(),
#         'subtotal': subtotal,
#         'discount_total': discount_total,
#         'total': total,
#         'applied_coupon': applied_coupon,
#         'shipping_cost': shipping_cost,
#         'discount_total': discount_total,
   
#     })



@login_required
def add_to_wishlist(request, products_id=None, variant_id=None):
    if products_id:
        product = get_object_or_404(Product, id=products_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    elif variant_id:
        variant = get_object_or_404(Variant, id=variant_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, variant=variant)

    if created:
        messages.success(request, "Item added to your wishlist!")
    else:
        messages.info(request, "Item is already in your wishlist.")
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    wishlist_item.delete()
    messages.success(request, "Item removed from your wishlist.")
    return redirect('wishlist')

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {'wishlist_items': wishlist_items}
    return render(request, 'wishlist.html', context)

@login_required
def manage_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Set the user to the logged-in user
            address.save()  # Save the address
            return redirect('checkout')  # Redirect after saving
    else:
        form = AddressForm()

    return render(request, 'manage_address.html', {'form': form})


  
@login_required
def manage_address_checkout(request, address_id=None):
    # Retrieve the address instance if address_id is provided; otherwise, create a new form instance
    if address_id:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        form = AddressForm(instance=address)  # Pre-fill the form with existing address data
    else:
        address = None
        form = AddressForm()  # Empty form for creating a new address

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)  # Bind the form with POST data
        if form.is_valid():
            form.save()  # Save the address (either update or create)
            messages.success(request, "Address updated successfully!" if address else "Address added successfully!")
            return redirect('checkout')  # Adjust the redirect URL as per your application

    context = {'form': form, 'address': address}
    return render(request, 'manage_address_checkout.html', context)

@login_required
def add_address_checkout(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('checkout')  # Redirect to profile page after adding address
    else:
        form = AddressForm()
    return render(request, 'manage_address_checkout.html', {'form': form})



 


 
 



# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.utils.timezone import now
# from decimal import Decimal
# from .models import Cart, Address, Order, OrderItem, UserCoupon
# from .forms import AddressForm
# from .utils import calculate_totals, create_razorpay_order
# from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt
# import razorpay

# @csrf_exempt
# @login_required
# def checkout(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     if not cart_items.exists():
#         messages.error(request, "Your cart is empty. Please add items before checkout.")
#         return redirect('cart')

#     coupon_id = request.session.get('applied_coupon_id')
#     subtotal, discount_total, coupon_discount, applied_coupon, shipping_cost, total = calculate_totals(cart_items, coupon_id, request.user)

#     # Convert total to integer for Razorpay order creation
#     total_paise = int(total * 100)

#     addresses = Address.objects.filter(user=request.user)

#     if request.method == 'POST':
#         selected_address_id = request.POST.get('address_id')
#         payment_method = request.POST.get('payment_method')
        
#         if selected_address_id:
#             address = get_object_or_404(Address, id=selected_address_id, user=request.user)
#             if payment_method == 'Online':
#                 # Generate Razorpay order
#                 razorpay_order = create_razorpay_order(total_paise)
#                 razorpay_order_id = razorpay_order['id']
#                 # Store Razorpay order details in session
#                 request.session['razorpay_order_id'] = razorpay_order_id
#                 request.session['payment_method'] = payment_method
#                 request.session['selected_address_id'] = selected_address_id

#                 return render(request, 'payment.html', {
#                     'razorpay_order_id': razorpay_order_id,
#                     'razorpay_key': settings.RAZORPAY_KEY_ID,
#                     'razorpay_amount': total_paise,  # Pass amount in paise
#                 })
#             else:
#                 request.session['payment_method'] = payment_method
#                 request.session['selected_address_id'] = selected_address_id
#                 return redirect('place_order_from_cart', address_id=address.id)

#     return render(request, 'checkout.html', {
#         'cart_items': cart_items,
#         'addresses': addresses,
#         'address_form': AddressForm(),
#         'subtotal': subtotal,
#         'discount_total': discount_total,
#         'coupon_discount': coupon_discount,
#         'total': total,
#         'applied_coupon': applied_coupon,
#         'shipping_cost': shipping_cost,
#     })


# @csrf_exempt
# @login_required
# def place_order_from_cart(request, address_id):
#     cart_items = Cart.objects.filter(user=request.user)
#     if not cart_items.exists():
#         messages.error(request, "Your cart is empty. Please add items before checkout.")
#         return redirect('cart')

#     coupon_id = request.session.get('applied_coupon_id')
#     subtotal, discount_total, coupon_discount, applied_coupon, shipping_cost, total = calculate_totals(cart_items, coupon_id, request.user)

#     address = get_object_or_404(Address, id=address_id, user=request.user)
#     payment_method = request.session.get('payment_method', 'COD')
#     razorpay_order_id = request.session.get('razorpay_order_id', '')

#     order = Order.objects.create(
#         user=request.user,
#         address=address,
#         total_price=total,
#         payment_method=payment_method,  # Use the payment method from the session
#         applied_coupon=applied_coupon,  # Add the applied coupon
#         razorpay_order_id=razorpay_order_id,
#         payment_status='Paid' if payment_method == 'Online' else 'Pending'  # Update payment status
#     )

#     for item in cart_items:
#         OrderItem.objects.create(
#             order=order,
#             variant=item.variant,
#             quantity=item.quantity,
#             price=item.variant.price,
#         )
#         item.variant.stock -= item.quantity
#         item.variant.save()

#     # Mark the coupon as used and update the usage count after the order is created successfully
#     if applied_coupon:
#         user_coupon = UserCoupon.objects.get(user=request.user, coupon=applied_coupon)
#         user_coupon.is_used = True
#         user_coupon.save()
#         applied_coupon.usage_count += 1
#         applied_coupon.save()

#     cart_items.delete()
#     request.session.pop('applied_coupon_id', None) 
#     request.session.pop('payment_method', None)
#     request.session.pop('razorpay_order_id', None)
#     request.session.pop('selected_address_id', None)

#     return redirect('order_confirmation', order_id=order.id)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from decimal import Decimal
from .models import Cart, Address, Order, OrderItem, UserCoupon, Wallet, WalletTransaction
from .forms import AddressForm
from .utils import calculate_totals, create_razorpay_order
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay

@csrf_exempt
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Please add items before checkout.")
        return redirect('cart')

    coupon_id = request.session.get('applied_coupon_id')
    subtotal, discount_total, coupon_discount, applied_coupon, shipping_cost, total = calculate_totals(cart_items, coupon_id, request.user)

    # Check if wallet amount is available
    wallet = Wallet.objects.get(user=request.user)
    wallet_amount = wallet.balance
    if wallet_amount > 0:
        if wallet_amount >= total:
            total = 0
        else:
            total -= wallet_amount

    # Convert total to integer for Razorpay order creation
    total_paise = int(total * 100)

    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        selected_address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        
        if selected_address_id:
            address = get_object_or_404(Address, id=selected_address_id, user=request.user)
            if payment_method == 'Online' and total_paise > 0:
                # Generate Razorpay order
                razorpay_order = create_razorpay_order(total_paise)
                razorpay_order_id = razorpay_order['id']
                # Store Razorpay order details in session
                request.session['razorpay_order_id'] = razorpay_order_id
                request.session['payment_method'] = payment_method
                request.session['selected_address_id'] = selected_address_id

                return render(request, 'payment.html', {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_key': settings.RAZORPAY_KEY_ID,
                    'razorpay_amount': total_paise,  # Pass amount in paise
                })
            else:
                request.session['payment_method'] = payment_method
                request.session['selected_address_id'] = selected_address_id
                return redirect('place_order_from_cart', address_id=address.id)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'addresses': addresses,
        'address_form': AddressForm(),
        'subtotal': subtotal,
        'discount_total': discount_total,
        'coupon_discount': coupon_discount,
        'total': total,
        'applied_coupon': applied_coupon,
        'shipping_cost': shipping_cost,
    })


@csrf_exempt
@login_required
def place_order_from_cart(request, address_id):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Please add items before checkout.")
        return redirect('cart')

    coupon_id = request.session.get('applied_coupon_id')
    subtotal, discount_total, coupon_discount, applied_coupon, shipping_cost, total = calculate_totals(cart_items, coupon_id, request.user)

    address = get_object_or_404(Address, id=address_id, user=request.user)
    payment_method = request.session.get('payment_method', 'COD')
    razorpay_order_id = request.session.get('razorpay_order_id', '')

    # Deduct wallet amount
    wallet = Wallet.objects.get(user=request.user)
    wallet_amount = wallet.balance
    if wallet_amount > 0:
        if wallet_amount >= total:
            wallet.deduct_funds(total)
            total = 0
            payment_status = 'Paid'
        else:
            total -= wallet_amount
            wallet.deduct_funds(wallet_amount)
            payment_status = 'Pending'
    else:
        payment_status = 'Pending'

    order = Order.objects.create(
        user=request.user,
        address=address,
        total_price=total,
        payment_method=payment_method,  # Use the payment method from the session
        applied_coupon=applied_coupon,  # Add the applied coupon
        razorpay_order_id=razorpay_order_id,
        payment_status=payment_status  # Update payment status
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            variant=item.variant,
            quantity=item.quantity,
            price=item.variant.price,
        )
        item.variant.stock -= item.quantity
        item.variant.save()

    # Mark the coupon as used and update the usage count after the order is created successfully
    if applied_coupon:
        user_coupon = UserCoupon.objects.get(user=request.user, coupon=applied_coupon)
        user_coupon.is_used = True
        user_coupon.save()
        applied_coupon.usage_count += 1
        applied_coupon.save()

    # Create a WalletTransaction for the wallet deduction
    if wallet_amount > 0:
        WalletTransaction.objects.create(
            user=request.user,
            amount=wallet_amount if wallet_amount < total else total,
            transaction_type='Purchase',
            description=f"Purchase for order {order.id}"
        )

    cart_items.delete()
    request.session.pop('applied_coupon_id', None)
    request.session.pop('payment_method', None)
    request.session.pop('razorpay_order_id', None)
    request.session.pop('selected_address_id', None)

    return redirect('order_confirmation', order_id=order.id)


@csrf_exempt
@login_required
def razorpay_payment_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        # Verify the payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            # Signature is valid, process the order
            address_id = request.session.get('selected_address_id')
            if address_id:
                return redirect('place_order_from_cart', address_id=address_id)
            else:
                messages.error(request, "Address ID not found in session.")
                return redirect('checkout')
        except razorpay.errors.SignatureVerificationError:
            # Signature verification failed
            messages.error(request, "Payment verification failed.")
            return redirect('checkout')
    return redirect('checkout')


@csrf_exempt
def razorpay_payment_failure(request):
    messages.error(request, "Payment failed. Please try again.")
    return redirect('checkout')


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {
        'order': order,
        'items': order.items.all(),  # Get the related OrderItems
    })


@login_required
def order_list(request):
    # Retrieve all orders for the logged-in user
    orders = request.user.orders.all().order_by('-created_at')  # Order by creation date, most recent first
    
    return render(request, 'order_list.html', {
        'orders': orders,
    })



@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status in ['Processing', 'Shipped']:
        order.status = 'Cancelled'
        order.save()
        messages.success(request, "Your order has been cancelled.")
    else:
        messages.error(request, "Order cannot be cancelled.")

    return redirect('order_list')

@login_required
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'Delivered':
        order.status = 'Returned'
        order.save()
        messages.success(request, "Your order has been returned.")
    else:
        messages.error(request, "Order cannot be returned.")

    return redirect('order_list')



def add_to_wallet(request, amount):
    wallet = request.user.wallet  # Assuming the user is logged in
    wallet.add_funds(amount)
    return HttpResponse(f"Added ₹{amount} to your wallet. New Balance: ₹{wallet.balance}")



 
@login_required
def view_profile(request):
    # Get the username of the logged-in user
    user=request.user
    
    request.user 
    addresses = user.addresses.all() 
    wallet, created = Wallet.objects.get_or_create(user=user) 
    return render(request, 'view_profile.html', { 
        'profile': user, 
        'addresses': addresses, 
        'wallet': wallet, 
        'wallet_transactions': user.wallet_transactions.all()
    })


from .models import Coupon,UserCoupon
from django.utils.timezone import now
 

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code') 
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_active and coupon.start_date <= now() <= coupon.end_date:
                # Fetch or create the UserCoupon object
                user_coupon, created = UserCoupon.objects.get_or_create(
                    user=request.user, coupon=coupon, defaults={'is_used': False}
                )

                if user_coupon.is_used:
                    messages.error(request, "This coupon has already been used.")
                else:
                   
                    
                    # Store the applied coupon in session
                    request.session['applied_coupon_id'] = coupon.id
                    messages.success(request, "Coupon applied successfully.")
            else:
                messages.error(request, "Coupon is not active or expired.")
        except Coupon.DoesNotExist:
            messages.warning(request, "Invalid Coupon.")
    return redirect('checkout')

 
                 
          

def remove_coupon(request):
    applied_coupon_id =request.session.pop('applied_coupon_id',None)
    if applied_coupon_id:
        user_coupon=UserCoupon.objects.filter(
            user=request.user, coupon_id=applied_coupon_id, is_used=True
        ).first()

        if user_coupon:
            user_coupon.is_used = False
            user_coupon.save()
            messages.success(request, 'Coupon removed successfully')
    else:

        messages.warning(request,"No Coupon applied")
    return redirect('checkout')



# views.py
# views.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order

def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)
    if status == 'Cancelled':
        try:
            order.cancel_order()
            messages.success(request, f"Order {order_id} cancelled successfully!")
        except ValueError as e:
            messages.error(request, str(e))
    elif status == 'Returned':
        try:
            order.return_order()
            messages.success(request, f"Order {order_id} returned successfully!")
        except ValueError as e:
            messages.error(request, str(e))
    else:
        messages.error(request, 'Invalid status')

    return redirect('order_list')  # Replace 'your_orders_page' with the name of your orders page URL
