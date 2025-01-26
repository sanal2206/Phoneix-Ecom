from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from .models import Product,Category,ProductImage,CustomUser,OtpToken,Address,Cart,Variant,Wishlist,Wallet,Coupon,UserCoupon,Order,OrderItem,ReturnRequest,Brand,TypeCategory,Offer
from django.db.models import Avg
from django.contrib.auth import get_user_model
from django .contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm,ReviewForm,AddressForm,UserProfileForm,ReturnRequestForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.db.models import F
from django.template import TemplateDoesNotExist
from django.core.exceptions import ValidationError

 
 


# Create your views here.

@login_required
def home(request):
    # Get the filter and sorting values from the GET request
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort_by', 'name_asc')
    
    # Get selected type category from GET request
    selected_type_category = request.GET.get('type_category', '')

    # Start with the basic query, filtering only active and non-deleted products
    products = Product.objects.filter(
    is_active=True, 
    is_deleted=False, 
    type_category__is_active=True,  # Ensure the type category is active
    category__is_active=True        # Ensure the category is active
        )

    # Filter by search query if provided
    if search_query:
        products = products.filter(name__icontains=search_query)

        if not products.exists():
            messages.info(request, "No products found matching your search.")
    
    # Handle brand filtering
    selected_brand = request.GET.get('brand', '')
    if selected_brand:
        products = products.filter(brand__name=selected_brand)

    # Handle type category filtering
    if selected_type_category:
        products = products.filter(type_category__name=selected_type_category)

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
        usercoupon__user=request.user,
        usage_count__lt=F('usage_limit')  # Ensure usage_count is less than usage_limit

    ).distinct()



    # Fetching all brands for the dropdown
    brands = Brand.objects.all()
    type_categories = TypeCategory.objects.filter(is_active=True)
    active_offers = Offer.active_offers() 

    return render(request, 'home.html', {
        'products': products,
        'search_query': search_query,
        'type_categories': type_categories,
        'selected_type_category': selected_type_category,
        'sort_by': sort_by,
        'available_coupons': available_coupons,
        'brands': brands,
        'active_offers': active_offers
    })


 

def brand_view(request, brand_name):
    brand_name = brand_name.lower()  # Ensure brand name is lowercase
    brand = Brand.objects.get(name=brand_name)  # Get the brand by name
    products = Product.objects.filter(brand=brand)  # Filter products by brand

    return render(request, 'your_template.html', {'products': products, 'brand': brand})


def about(request):
    try:
        return render(request, 'about.html')
    except TemplateDoesNotExist:
        return render(request, '404.html', status=404)


 

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
    form = SignUpForm()
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            form.save()
            gmail_id = form.cleaned_data['email']  # Assign to gmail_id variable
            request.session['gmail_id'] = gmail_id  # Store Gmail ID in session
            
            messages.success(request, 'Account created successfully. An OTP has been sent to your email.')
            return redirect('verify-email', username=request.POST['username'])
    
    # Print the email stored in the session (if available) after processing the request
    if 'gmail_id' in request.session:
        print(f"Stored email in session: {request.session['gmail_id']}")
    
    context = {'form': form}
    return render(request, 'register.html', context)


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

 
import logging
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import OtpToken  # Replace with your actual OTP model

logger = logging.getLogger(__name__)
COOLDOWN_PERIOD = 5
def resend_otp(request):
    if request.method == 'POST':
        # Retrieve the email from the session
        user_email = request.session.get('gmail_id')
        if not user_email:
            logger.warning("No email found in the session for resending OTP.")
            return JsonResponse({'success': False, 'message': "No email found for resending OTP."})

        try:
            # Get the user by email
            User = get_user_model()
            user = User.objects.filter(email=user_email).first()
            if not user:
                return JsonResponse({'success': False, 'message': "User not found."})


            from .models import OtpToken  # Import your OTP model
            # Check the last OTP generated for the user
            last_otp = OtpToken.objects.filter(user=user).order_by('-otp_expires_at').first()

            if last_otp:
                time_since_last_otp = (timezone.now() - last_otp.otp_created_at).total_seconds()
                cooldown_seconds = COOLDOWN_PERIOD * 60

                if time_since_last_otp < cooldown_seconds:
                    remaining_time = int(cooldown_seconds - time_since_last_otp)
                    minutes, seconds = divmod(remaining_time, 60)
                    return JsonResponse({
                        'success': False,
                        'message': f"Please wait {minutes} minutes and {seconds} seconds before requesting a new OTP."
                    })
                

            
            # Generate a new OTP
            otp = OtpToken.objects.create(
                user=user,
                otp_expires_at=timezone.now() + timezone.timedelta(minutes=5)
            )

            # Send OTP to the user's email
            subject = "Resend OTP Verification"
            message = f"Hi {user.username}, your OTP is {otp.otp_code}. It will expire in 5 minutes."
            sender = "sanalsabu22@example.com"  # Replace with your sender email
            receiver = [user.email]

            send_mail(subject, message, sender, receiver, fail_silently=False)

            logger.info(f"OTP resent to {user.email}")
            return JsonResponse({'success': True, 'message': "OTP resent successfully."})
        except Exception as e:
            logger.error(f"Error resending OTP: {e}")
            return JsonResponse({'success': False, 'message': "Failed to resend OTP. Please try again later."})

    return JsonResponse({'success': False, 'message': "Invalid request method."})



from django.db.models import Q
@login_required
def product(request, pk):
    # Get the product by primary key (id)
    products = get_object_or_404(Product, id=pk, is_active=True, is_deleted=False)

    offer_details=None
    if products.type_category:
        active_offer=Offer.objects.filter(type_category=products.type_category,is_active=True).first()

        if active_offer:
            offer_details=active_offer
    
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
        'variants': variants,  # Include the product variants
        'offer_details': offer_details,

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
    return render(request, 'manage_address_profile.html', {'form': form})


@login_required
def delete_address(request, address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")

    return redirect('user_profile')  # Redirect to profile page after deleting address    


from allauth.socialaccount.models import SocialAccount  # Import this if you're using Django Allauth

def is_social_account(user):
    return SocialAccount.objects.filter(user=user).exists()


@login_required
def update_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        profile_photo = request.FILES.get('profile_photo')  # Get the uploaded image
        password = request.POST.get('password')  # Password entered by the user for confirmation

        user = request.user

        if is_social_account(user):
            # Skip password check for social accounts
            messages.success(request, "Social account detected. Updating profile directly.")
        else:
            if not user.check_password(password):  # Check if the password is correct
                messages.error(request, "Incorrect password. Please try again.")
                return redirect('update_profile')


        if CustomUser.objects.exclude(id=user.id).filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different one.')
            return redirect('update_profile')        

        # Update the logged-in user's profile
        user.username = username
        user.phone_number = phone_number  # Ensure your user model includes this field
        if profile_photo:
            user.profile_photo = profile_photo


        try:
            user.full_clean()
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('update_profile')  # Display the errors if any        
        
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
        messages.warning(request, f"Sorry, we only have {variant.stock} units of this variant in stock.")
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



# from decimal import Decimal

# def view_cart(request):
#     cart_items = Cart.objects.filter(user=request.user)

#     # Calculate subtotal (price without discount) and discount total
#     subtotal = sum(Decimal(item.variant.price) * item.quantity for item in cart_items)
#     discount_total = sum(
#         (Decimal(item.variant.price) * (Decimal(item.variant.product.discount) / 100)) * item.quantity
#         for item in cart_items if item.variant.product.discount > 0
#     )
    
    

#     # Convert shipping cost to Decimal
#     shipping_cost = Decimal('5.00')

#     # Calculate final total (subtotal - discount + shipping)
#     total = subtotal - discount_total + shipping_cost

#     return render(request, 'cart.html', {
#         'cart_items': cart_items,
#         'subtotal': subtotal,
#         'discount_total': discount_total,
#         'total': total,
#     })

from decimal import Decimal

def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    # Calculate subtotal (price without discount) and discount total
    subtotal = sum(Decimal(item.variant.price) * item.quantity for item in cart_items)
    
    discount_total = Decimal(0)  # Initialize discount total

    for item in cart_items:
        product_price = Decimal(item.variant.price)
        product_discount = Decimal(item.variant.product.discount)
        type_category_offer_discount = Decimal(0)  # Default discount for TypeCategory offer

        # Apply product-specific discount (if any)
        product_discount_value = (product_price * product_discount / 100) * item.quantity
        discount_total += product_discount_value

        # Apply TypeCategory offer (if any)
        if item.variant.product.type_category:
            # Get the active offer for the TypeCategory
            offer = Offer.objects.filter(type_category=item.variant.product.type_category, is_active=True).first()
            if offer:
                 
                if offer.offer_type == 'percentage':
                    type_category_offer_discount = (product_price * offer.discount_value / 100) * item.quantity
                elif offer.offer_type == 'flat':
                    type_category_offer_discount = offer.discount_value * item.quantity

            

                # Add to the discount total
                discount_total += type_category_offer_discount
            
 
    # Convert shipping cost to Decimal
    shipping_cost = Decimal('5.00')

    # Calculate final total (subtotal - discount + shipping)
    total = subtotal - discount_total + shipping_cost
    print(f"Subtotal: {subtotal}, Discount Total: {discount_total}, Shipping: {shipping_cost}, Total: {total}")

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



 
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Cart

from decimal import Decimal
# def update_cart_quantity(request, item_id):
#     if request.method == 'POST':
#         try:
#             # Get the cart item for the current user
#             cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
#             data = json.loads(request.body)
#             quantity = data.get('quantity', 1)
#             quantity = int(quantity)

#             # Check stock and quantity limits
#             if quantity > cart_item.variant.stock:
#                 return JsonResponse({'success': False, 'error': f"Only {cart_item.variant.stock} units available in stock."})
#             elif quantity > 5:
#                 return JsonResponse({'success': False, 'error': "You are allowed to add a maximum of 5 items to the cart."})
#             elif quantity < 1:
#                 return JsonResponse({'success': False, 'error': "Quantity must be at least 1."})
#             else:
#                 # Update the cart item's quantity
#                 cart_item.quantity = quantity
#                 cart_item.save()

#                 # Calculate new totals
#                 subtotal = sum(
#                     Decimal(item.variant.price) * Decimal(item.quantity) for item in Cart.objects.filter(user=request.user)
#                 )
#                 discount_total = sum(
#                     (Decimal(item.variant.price) * (Decimal(item.variant.product.discount) / 100) * Decimal(item.quantity))
#                     for item in Cart.objects.filter(user=request.user) if item.variant.product.discount > 0
#                 )

                

                
#                 shipping_cost = Decimal(5.00)  # Use Decimal for shipping cost

#                 # Calculate the total
#                 total = subtotal - discount_total + shipping_cost

#                 return JsonResponse({
#                     'success': True,
#                     'subtotal': str(subtotal),  # Convert to string for JSON response
#                     'discount_total': str(discount_total),  # Convert to string for JSON response
#                     'total': str(total),  # Convert to string for JSON response
#                     'item_total': str(Decimal(cart_item.variant.price) * Decimal(quantity)),  # Convert to string for JSON response
#                 })

#         except ValueError:
#             return JsonResponse({'success': False, 'error': "Invalid quantity."})
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})

#     return JsonResponse({'success': False, 'error': "Invalid request method."})

def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        try:
            # Get the cart item for the current user
            cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
            data = json.loads(request.body)
            quantity = data.get('quantity', 1)
            quantity = int(quantity)

            # Check stock and quantity limits
            if quantity > cart_item.variant.stock:
                return JsonResponse({'success': False, 'error': f"Only {cart_item.variant.stock} units available in stock."})
            elif quantity > 5:
                return JsonResponse({'success': False, 'error': "You are allowed to add a maximum of 5 items to the cart."})
            elif quantity < 1:
                return JsonResponse({'success': False, 'error': "Quantity must be at least 1."})
            else:
                # Update the cart item's quantity
                cart_item.quantity = quantity
                cart_item.save()

                # Calculate new totals
                subtotal = sum(
                    Decimal(item.variant.price) * Decimal(item.quantity) for item in Cart.objects.filter(user=request.user)
                )
                discount_total = Decimal(0)  # Initialize discount total

                for item in Cart.objects.filter(user=request.user):
                    # Check for product discount
                    if item.variant.product.discount > 0:
                        discount_total += (Decimal(item.variant.price) * (Decimal(item.variant.product.discount) / 100) * Decimal(item.quantity))
                    
                    # Check for type_category offers
                    if item.variant.product.type_category:
                        # Get the active offer for the TypeCategory
                        offer = Offer.objects.filter(type_category=item.variant.product.type_category, is_active=True).first()
                        if offer:
                            product_price = Decimal(item.variant.price)
                            type_category_offer_discount = Decimal(0)

                            if offer.offer_type == 'percentage':
                                type_category_offer_discount = (product_price * offer.discount_value / 100) * item.quantity
                            elif offer.offer_type == 'flat':
                                type_category_offer_discount = offer.discount_value * item.quantity

                            # Add to the discount total
                            discount_total += type_category_offer_discount

                shipping_cost = Decimal(5.00)  # Use Decimal for shipping cost

                # Calculate the total
                total = subtotal - discount_total + shipping_cost

                return JsonResponse({
                    'success': True,
                    'subtotal': str(subtotal),  # Convert to string for JSON response
                    'discount_total': str(discount_total),  # Convert to string for JSON response
                    'total': str(total),  # Convert to string for JSON response
                    'item_total': str(Decimal(cart_item.variant.price) * Decimal(quantity)),  # Convert to string for JSON response
                })

        except ValueError:
            return JsonResponse({'success': False, 'error': "Invalid quantity."})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': "Invalid request method."})


 



@login_required
def add_to_wishlist(request, products_id, variant_id):
    # Retrieve the product using the provided product_id
    product = get_object_or_404(Product, id=products_id)
    print(product)
    
    # Ensure the variant exists and belongs to the selected product
    variant = get_object_or_404(Variant, id=variant_id, product=product)
    print(variant)

    # Check if the product-variant combination already exists in the user's wishlist
    if Wishlist.objects.filter(user=request.user, product=product, variant=variant).exists():
        # Optionally, show a message or just redirect
        return redirect('wishlist')  # Redirect to wishlist page

    # Add the selected product-variant combination to the wishlist
    Wishlist.objects.create(user=request.user, product=product, variant=variant)
    
    return redirect('wishlist')  # Redirect to wishlist page


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

    return render(request, 'manage_address_checkout.html', {'form': form})


  
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



 


 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Cart, Address, Order, OrderItem, UserCoupon, Wallet, WalletTransaction
from .forms import AddressForm
from .utils import calculate_totals, create_razorpay_order
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import razorpay

from django.http import JsonResponse

@csrf_exempt
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('variant')
    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Please add items before checkout.")
        return redirect('cart')
    
    for item in cart_items:
        if item.variant.stock < item.quantity:
            messages.error(request, f"Not enough stock for {item.variant.product}. Only {item.variant.stock} units available.")
            return redirect('view_cart')

    coupon_id = request.session.get('applied_coupon_id')
    subtotal, discount_total, coupon_discount, applied_coupon, shipping_cost, total = calculate_totals(cart_items, coupon_id, request.user)

    # Check if wallet amount is available
    # wallet = Wallet.objects.get(user=request.user)
    # wallet_amount = wallet.balance
    # if wallet_amount > 0:
    #     if wallet_amount >= total:
    #         total = 0
    #     else:
    #         total -= wallet_amount

    # # Convert total to integer for Razorpay order creation
    # total_paise = int(total * 100)

    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        selected_address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        use_wallet = 'use_wallet' in request.POST 
        # Store wallet usage preference in session 
        request.session['use_wallet'] = use_wallet

        wallet = Wallet.objects.get(user=request.user)
        wallet_amount = wallet.balance if use_wallet else 0

        if wallet_amount > 0:

            if wallet_amount>=total:
                total=0
            else:
                total -= wallet_amount
                 
        total_paise = int(total * 100)
        request.session['total_amount'] = float(total) # Store the updated total in the session
                          
        if selected_address_id:
            address = get_object_or_404(Address, id=selected_address_id, user=request.user)
            
            # Restrict COD for orders above ₹1000
            if payment_method == 'COD' and total > 1500:
                messages.error(request, "Cash on Delivery is not available for orders above ₹1500.")
                return redirect('checkout')

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

    address_snapshot={
        'user':request.user.id,
        'address_line_1':address.address_line_1,
        'address_line_2':address.address_line_2,
        'city':address.city,
        'state':address.state,
        'postal_code':address.postal_code,
        'country':address.country,
    }

    payment_method = request.session.get('payment_method', 'COD')
    razorpay_order_id = request.session.get('razorpay_order_id', '')

    # Deduct wallet amount
    use_wallet = request.session.get('use_wallet', False)
    wallet = Wallet.objects.get(user=request.user)
    wallet_amount = wallet.balance if use_wallet else 0
    print(wallet_amount)
    wallet_amount_used = 0
    if wallet_amount > 0:
        if wallet_amount >= total:
            wallet.deduct_funds(total)
            wallet_amount_used = total
            total = 0
        else:
            wallet_amount_used=wallet_amount
            wallet.deduct_funds(wallet_amount)
            total -= wallet_amount

    if total==0:
        payment_status="Paid"
    elif payment_method=="Online":
        razorpay_payment_id=request.session.get('razorpay_payment_id',None)
        if razorpay_payment_id:
            payment_status="Paid"
        else:
            payment_status="Failed"
    elif payment_method=="COD":
        payment_status="Pending"                        
     
     

    order = Order.objects.create(
        user=request.user,
        address=address,
        address_snapshot=address_snapshot,  # Save the address snapshot
        total_price=total,
        wallet_amount_used=wallet_amount_used,
        payment_method=payment_method,  # Use the payment method from the session
        applied_coupon=applied_coupon,  # Add the applied coupon
        razorpay_order_id=razorpay_order_id,
        payment_status=payment_status  # Update payment status
    )




    for item in cart_items:

        discounted_price = Decimal(item.variant.price)

        # Apply product discount (if any)
        if item.variant.product.discount > 0:
            discounted_price -= (discounted_price * Decimal(item.variant.product.discount) / 100)

        # Check for type_category offers
        if item.variant.product.type_category:
            offer = Offer.objects.filter(
                type_category=item.variant.product.type_category, is_active=True
            ).first()

            if offer:
                # Calculate the offer discount based on offer type
                if offer.offer_type == 'percentage':
                    discounted_price -= (discounted_price * Decimal(offer.discount_value) / 100)
                elif offer.offer_type == 'flat':
                    discounted_price -= Decimal(offer.discount_value)

        # Create the OrderItem with the final discounted price
        print(discounted_price)
        OrderItem.objects.create(
            order=order,
            variant=item.variant,
            quantity=item.quantity,
            price=discounted_price,  
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
    if wallet_amount_used > 0:
        WalletTransaction.objects.create(
            user=request.user,
            amount=wallet_amount_used,
            transaction_type='Purchase',
            description=f"Purchase for order {order.id}"
        )


    if payment_status == "Failed":
        messages.error(request, "Payment failed. Please complete the payment from the 'My Orders' page.")
        return redirect('checkout') 
    
    cart_items.delete()
    request.session.pop('applied_coupon_id', None)
    request.session.pop('payment_method', None)
    request.session.pop('razorpay_order_id', None)
    request.session.pop('selected_address_id', None)
    request.session.pop('total_amount', None) 
    request.session.pop('use_wallet', None)

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
            request.session['razorpay_payment_id'] = payment_id
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


 

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order, Product, Variant, OrderItem

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status in ['Processing', 'Shipped']:
        order.status = 'Cancelled'
        order.save()
        
        # Update stock
        for item in order.items.all():
            variant = item.variant
            variant.stock += item.quantity
            variant.save()
        
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
        
        # Update stock
        for item in order.items.all():
            variant = item.variant
            variant.stock += item.quantity
            variant.save()
        
        messages.info(request, "Your order has been returned.")
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
            messages.info(request, 'Coupon removed successfully')
    else:

        messages.warning(request,"No Coupon applied")
    return redirect('checkout')



# views.py
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Order, OrderItem

@csrf_exempt
@login_required
def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if status not in ['Cancelled', 'Returned']:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    if status == 'Cancelled' and order.status in ['Processing', 'Shipped']:
        order.status = 'Cancelled'
    elif status == 'Returned' and order.status == 'Delivered':
        order.status = 'Returned'
    else:
        return JsonResponse({'error': 'Order cannot be updated'}, status=400)
    
    order.save()

    # Update stock
    for item in order.items.all():
        variant = item.variant
        variant.stock += item.quantity
        variant.save()

    return JsonResponse({'success': 'Order status updated'})


 
 
 
 #wallet Transaction

@login_required
def wallet_transactions(request):
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'wallet_transactions.html', {'transactions': transactions})

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa

def download_invoice(request, order_id):
    # Fetch order and related details
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()  # Adjust this based on your related_name
    user = request.user

    # Render HTML for the invoice
    html = render_to_string('invoice_template.html', {
        'order': order,
        'items': items,
        'user': user,
    })

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors generating the invoice.', status=500)
    return response




#test
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import OrderItem, ReturnRequest

def submit_return(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    # Ensure the order is eligible for return
    if item.order.status != 'Delivered':
        messages.error(request, 'Only items from delivered orders can be returned.')
        return redirect('order_confirmation', order_id=item.order.id)

    # Ensure no duplicate return request exists
    if ReturnRequest.objects.filter(order_item=item).exists():
        messages.warning(request, 'A return request for this item already exists.')
        return redirect('order_confirmation', order_id=item.order.id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        if not reason:
            messages.error(request, 'Please provide a reason for your return.')
            return render(request, 'submit_return.html', {'item': item})

        # Create the return request with the user association
        ReturnRequest.objects.create(
            order_item=item,
            reason=reason,
            user=request.user  # Associate the return request with the user
        )
        messages.success(request, 'Your return request has been submitted successfully!')
        return redirect('order_confirmation', order_id=item.order.id)

    return render(request, 'submit_return.html', {'item': item})

 

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import OrderItem, Order

@login_required
def cancel_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    # Check if the order status allows cancellation
    if item.order.status not in ['Cancelled', 'Delivered']:
        if not item.is_cancelled:
            try:
                # Start a transaction to ensure consistency
                with transaction.atomic():
                    # Mark the item as cancelled
                    item.is_cancelled = True
                    item.save()

                    # Restore stock for the associated variant
                    item.variant.stock += item.quantity
                    item.variant.save()

                    # Check if all items in the order are cancelled
                    order = item.order
                    if all(order_item.is_cancelled for order_item in order.items.all()):
                        order.status = 'Cancelled'
                        order.save()

                messages.success(
                    request,
                    f"Order item {item.variant.product.name} has been cancelled."
                )
            except Exception as e:
                messages.error(request, f"An error occurred while cancelling the item: {e}")
        else:
            messages.warning(request, "This item is already cancelled.")
    else:
        messages.error(
            request,
            "This order item cannot be cancelled as the order is already delivered or cancelled."
        )

    # Redirect to the order confirmation page
    return redirect('order_confirmation', order_id=item.order.id)


#page not found
def custom_404(request,exception):
    return render(request, '404.html',status=404)