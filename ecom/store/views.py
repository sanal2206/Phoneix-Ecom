from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,Category,ProductImage,CustomUser,OtpToken
from django.db.models import Avg
from django.contrib.auth import get_user_model
from django .contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm,ReviewForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail

# Create your views here.

def home(request):
    products=Product.objects.filter(is_active=True,is_deleted=False)
     
    # Calculate the average rating for each product
    for product in products:
        avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']
        product.avg_rating = round(avg_rating, 1) if avg_rating else 0
        product.stars_range = range(1, 6)  # Create a range from 1 to 5 for stars

    return render(request,'home.html',{'products':products })





def about(request):
    return render(request,'about.html',{})


# def login_user(request):
#     if request.method=="POST":
#         username=request.POST['username']
#         password=request.POST['password']
#         user = authenticate(username=username, password=password)  # Could be a coroutine

#         if user is not None:
#             login(request,user)
#             messages.success(request,("You have been logged in"))
#             return redirect('home')

#         else:
#             messages.success(request,'There was an error')
#             return redirect('login')
    
#     else:

#         return render(request,'login.html',{})

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


# @login_required
def product(request, pk):
    # Get the product by primary key (id)
    products = get_object_or_404(Product, id=pk, is_active=True,is_deleted=False)
    
    # Fetch images for the product
    images = ProductImage.objects.filter(product=products)


    # variants = products.variants.all() 
    variants = products.variants.filter(is_active=True)
     
    # Get related products (same category but excluding the current product)
    related_products = Product.objects.filter(category=products.category,is_active=True).exclude(pk=pk)[:4]  # Show up to 4 related products
    

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
            review = form.save(commit=False)
            review.product = products  # Associate the review with the current product
            review.user = request.user  # Associate the review with the logged-in user
            review.save()  # Save the review to the database
            return redirect('product', pk=products.id)  # Redirect to the same product page after saving the review

    context = {
        'products': products,
        'images': images,
        'related_products': related_products,
        'reviews': reviews,
        'form': form,  # Include the form for adding reviews
        'avg_rating': avg_rating,  # Pass the average rating to the template
        'variants':variants
         
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
    
    