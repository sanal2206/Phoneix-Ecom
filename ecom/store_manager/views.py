from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render
from store.models import Product, CustomUser, Category,ProductImage,Colour,Variant,Storage,Order,OrderItem
from django.contrib.auth.views import LoginView
from store.forms import ReviewForm
from .forms import ProductForm, ProductImageFormSet,ColourForm,VariantForm,StorageForm,CategoryForm


class AdminLoginView(LoginView):
    template_name = 'admin_login.html'

    def form_valid(self, form):
        user = form.get_user()
        if user.is_staff or user.is_superuser:
            login(self.request, user)
            return redirect('admin_dashboard')
        else:
            return HttpResponseForbidden("You are not authorized to access this area.")


def admin_dashboard(request):

    total_users = CustomUser.objects.count()  # Count of all users
    total_categories = Category.objects.count()  # Count of all categories
    total_products = Product.objects.count()  # Count of all products
    total_variants=Variant.objects.count()
    total_orders=Order.objects.count()
     
    context = {
        'total_users': total_users,
        'total_categories': total_categories,
        'total_products': total_products,
        'total_variants':total_variants,
        'total_orders':total_orders,
    }
         
    
    return render(request, 'dashboard.html', context)



def logout_user(request):
    logout(request)
    messages.success(request,('You have been logged out...Thanks for shopping'))
    return redirect('admin_login')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

def admin_user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


def admin_toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:  # Prevent admin from blocking superusers
        messages.error(request, "Cannot block/unblock a superuser!")
        return redirect('admin_user_list')

    user.is_active = not user.is_active
    user.save()
    status = "unblocked" if user.is_active else "blocked"
    messages.success(request, f"User {user.email} has been {status}.")
    return redirect('admin_user_list')


def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST['username']
        user.phone_number = request.POST['phone_number']
        user.address = request.POST['address']
        user.save()
        messages.success(request, 'User details updated successfully.')
        return redirect('admin_user_list')
    return render(request, 'edit_user.html', {'user': user})


def admin_delete_user(request, user_id):  
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:  # Prevent admin from deleting superusers
        messages.error(request, "Cannot delete a superuser!")
        return redirect('admin_user_list')

      # Permanently delete the user
    user.delete()
    messages.success(request, f"User {user.email} has been permanently deleted.")
    return redirect('admin_user_list')
 





 # store_manager/views.py
 

 
#product
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        image_formset = ProductImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.none())

        if product_form.is_valid() and image_formset.is_valid():
            # Save the product
            product = product_form.save()

            # Save the images
            for image_form in image_formset:
                if image_form.cleaned_data:  # Ensure it's not empty
                    image = image_form.save(commit=False)
                    image.product = product
                    image.save()

            return redirect('product_list')
    else:
        product_form = ProductForm()
        image_formset = ProductImageFormSet(queryset=ProductImage.objects.none())

    return render(request, 'add_product.html', {
        'product_form': product_form,
        'image_formset': image_formset,
    })

 

def product_list(request, product_id=None):
    if product_id:
        # Filter the products by product_id if provided
        products = Product.objects.filter(id=product_id)
    else:
        # Fetch all products
        products = Product.objects.filter(is_deleted=False).prefetch_related('images')

       
    return render(request, 'product_list.html', {'products': products})





# Edit Product View
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect to the product list page
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'edit_product.html', {'form': form, 'product': product})



# Deactivate/Activate Product View
def deactivate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Toggle product active status
    product.is_active = not product.is_active
    product.save()
    
    return redirect('product_list')  # Redirect to the product list page




def soft_delete_product(request, pk):
    if request.method == "POST":
        product = get_object_or_404(Product, pk=pk)
        product.is_deleted = True
        product.save()
        messages.success(request, f"Product '{product.name}' has been deleted successfully.")
        return redirect('product_list')  # Replace with your product list URL name
 

def add_color(request):
    if request.method == 'POST':
        form = ColourForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('color_list')  # Redirect to a list of colors or another page
    else:
        form = ColourForm()

    return render(request, 'add_color.html', {'form': form})


#color 

def color_list(request):
    colors = Colour.objects.all()
    return render(request, 'color_list.html', {'colors': colors})



def add_variant(request):
    if request.method == 'POST':
        variant_form = VariantForm(request.POST)

        if variant_form.is_valid():
            # Save the new variant
            variant = variant_form.save()
            messages.success(request, "Variant created successfully!")
            return redirect('variant_list')

    else:
        variant_form = VariantForm()

    return render(request, 'add_variant.html', {
        'variant_form': variant_form,
    })    

 

def variant_list(request):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        variant = get_object_or_404(Variant, id=variant_id)
        variant.is_active = not variant.is_active  # Toggle the is_active status
        variant.save()

    variants=Variant.objects.all()
    return render(request,'variant_list.html',{'variants':variants})



 
from django.urls import reverse


def deactivate_variant(request, variant_id):
    if request.method == 'POST':
        # Fetch the variant
        variant = get_object_or_404(Variant, id=variant_id)
        
        # Toggle the is_active status
        variant.is_active = not variant.is_active
        variant.save()

        # Redirect back to the product list page or another page
        product_id = variant.product.id  # Get the related product's ID
        return redirect(reverse('product_list', kwargs={'product_id': product_id}))

    # If not a POST request, redirect back to product list
    return redirect('product_list')



def edit_variant(request,variant_id):
    variant=get_object_or_404(Variant,id=variant_id)

    if request.method=="POST":
        form=VariantForm(request.POST,instance=variant)

        if form.is_valid():
            form.save()
            return redirect('variant_list')

    else:
        form=VariantForm(instance=variant)   

    return render(request,'edit_variant.html',{'form':form,'variant':variant})         

def add_storage(request):
    if request.method=='POST':
           
           form=StorageForm(request.POST)
           if form.is_valid():
               form.save()
               return redirect('storage_list')
    else:
           form=StorageForm()       

    return render(request,'add_storage.html',{'form':form})
        


def storage_list(request):

    storage=Storage.objects.all()

    return render(request,'list_storage.html',{'storage':storage})


# View to deactivate storage
def deactivate_storage(request, storage_id):
    storage = get_object_or_404(Storage, id=storage_id)
    storage.is_active = False
    storage.save()
    return redirect('storage_list')  # Redirect to the list view

# View to activate storage
def activate_storage(request, storage_id):
    storage = get_object_or_404(Storage, id=storage_id)
    storage.is_active = True
    storage.save()
    return redirect('storage_list')  # Redirect to the list view



    #category
 

def category_list(request):

    categories=Category.objects.all()

    return render(request,'category_list.html',{'categories':categories})


def deactivate_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.is_active = False
    category.save()
    return redirect('category_list')  # Replace with your category list view URL

def activate_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.is_active = True
    category.save()
    return redirect('category_list')  # Replace with your category list view URL


#deleted products
def deleted_product_list(request):
    deleted_products = Product.objects.filter(is_deleted=True)  # Fetch only deleted products
    return render(request, 'deleted_product.html', {'deleted_products': deleted_products})

def restore_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_deleted=True)
    product.is_deleted = False
    product.save()
    return redirect('deleted_product_list')

def permanent_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_deleted=True)
    product.delete()  # Permanently delete from the database
    return redirect('deleted_product_list')


def delete_variant(request, variant_id):
    # Retrieve the variant object safely
    variant = get_object_or_404(Variant, id=variant_id)
    variant.delete()  # Delete the object from the database

    return redirect('variant_list')
    

# views.py

# views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from store.models import Order, WalletTransaction

# Define allowed transitions
STATUS_TRANSITIONS = {
    'Pending': ['Confirmed', 'Cancelled'],
    'Confirmed': ['Shipped', 'Cancelled'],
    'Shipped': ['Delivered'],
    'Delivered': ['Returned'],
    'Cancelled': ['Pending'],
    'Returned': ['Delivered']
}

def store_manager_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        
        try:
            # Fetch the order
            order = get_object_or_404(Order, id=order_id)

            # Check if the new status is valid and can be transitioned to
            current_status = order.status
            if new_status in dict(Order.STATUS_CHOICES):
                # Prevent invalid transitions
                if current_status in STATUS_TRANSITIONS and new_status not in STATUS_TRANSITIONS[current_status]:
                    messages.error(request, f"Cannot change status from {current_status} to {new_status}.")
                else:
                    # Update the status
                    order.status = new_status
                    order.save()

                    # Handle stock adjustment if the order is canceled or returned
                    if current_status != 'Cancelled' and new_status == 'Cancelled':
                        for item in order.items.all():
                            item.variant.stock += item.quantity
                            item.variant.save()
                        order.user.wallet.add_funds(order.total_price)
                        WalletTransaction.objects.create(
                            user=order.user,
                            amount=order.total_price,
                            transaction_type='Refund',
                            description=f"Refund for cancelled order {order.id}"
                        )
                    elif current_status == 'Cancelled' and new_status == 'Pending':
                        for item in order.items.all():
                            item.variant.stock -= item.quantity
                            item.variant.save()
                        order.user.wallet.deduct_funds(order.total_price)
                        WalletTransaction.objects.create(
                            user=order.user,
                            amount=-order.total_price,
                            transaction_type='Purchase',
                            description=f"Reversal for order {order.id} being set to {new_status}"
                        )
                    elif new_status == 'Returned':
                        for item in order.items.all():
                            item.variant.stock += item.quantity
                            item.variant.save()

                    messages.success(request, f"Order #{order.id} status updated to {new_status}.")
            else:
                messages.error(request, "Invalid status provided.")
        except Exception as e:
            messages.error(request, f"Error updating order: {str(e)}")

        return redirect('store_manager_orders')

    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'store_manager_orders.html', {'orders': orders})

 

def store_manager_order_detail(request, order_id):
    # Fetch the specific order
    order = get_object_or_404(Order, id=order_id)

    return render(request, 'store_manager_order_detail.html', {'order': order})

from django.db.models import Q
from django.db.models import Avg
def Product_detail(request, pk):
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

    return render(request, 'product_detail.html', context)

 
from django.shortcuts import render
from django.db.models import Sum
from datetime import date, timedelta
from django.template.loader import render_to_string
from store.models import Order
from .utils import export_to_excel, export_to_pdf



 

def generate_sales_report(request):
    report_type = request.GET.get('report_type', 'total')
    start_date = end_date = None

    # Define date ranges based on the report type
    if report_type == 'daily':
        start_date = date.today()
        end_date = date.today()
    elif report_type == 'weekly':
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()
    elif report_type == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

    if start_date and end_date:
        # Filter orders within the date range
        orders = Order.objects.filter(created_at__date__range=[start_date, end_date])
    else:
        # Default to showing all orders
        orders = Order.objects.all()
        
    # Calculate metrics
    total_sales_count = orders.count()
    overall_order_amount = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_coupon_deductions = orders.aggregate(Sum('wallet_amount_used'))['wallet_amount_used__sum'] or 0

    context = {
        'total_sales_count': total_sales_count,
        'overall_order_amount': overall_order_amount,
        'total_coupon_deductions': total_coupon_deductions,
        'start_date': start_date,
        'end_date': end_date,
        'report_type': report_type
    }

    # Handle export requests
    if 'export' in request.GET:
        export_type = request.GET.get('export')
        if export_type == 'pdf':
            html_content = render_to_string('sales_report.html', context)
            return export_to_pdf(html_content)
        elif export_type == 'excel':
            return export_to_excel(context)

    return render(request, 'sales_report.html', context)
