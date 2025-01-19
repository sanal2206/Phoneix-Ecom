from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path("verify-email/<slug:username>", views.verify_email, name="verify-email"),
    path("resend-otp", views.resend_otp, name="resend-otp"),
    path('product/<int:pk>', views.product, name='product'),
    path('category/<str:cat>', views.category, name='category'),
    path('brand/<str:brand_name>/', views.brand_view, name='brand'),  # URL for brand filter


    # Profile
    path('profile/', views.user_profile, name='user_profile'),
    path('add-address/', views.add_address, name='add_address'),
    # path('manage-address/', views.manage_address, name='add_address'),
    path('manage-address-profile/<int:address_id>/', views.manage_address_profile, name='manage_address_profile'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('update-profile/', views.update_profile, name='update_profile'),

    # Cart
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/', views.view_cart, name='view_cart'),
    re_path(r'^add-to-cart/(?P<product_id>\d+)/(?P<variant_id>[\w-]+)/$', views.add_to_cart, name='add_to_cart'),

    # Checkout
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('manage-address-checkout/<int:address_id>/', views.manage_address_checkout, name='manage_address_checkout'),
    path('add-address-checkout/', views.add_address_checkout, name='add_address_checkout'),

    # Order
    path('place_order_from_cart/<int:address_id>/', views.place_order_from_cart, name='place_order_from_cart'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_list, name='order_list'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('update_order_status/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),

    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    # path('wishlist/add/<int:products_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('add-to-wishlist/<int:products_id>/<int:varinat_id>', views.add_to_wishlist,name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('view_profile/', views.view_profile, name='view_profile'),

    # Payment
    path('payment/success/', views.razorpay_payment_success, name='razorpay_payment_success'),
    path('payment/failure/', views.razorpay_payment_failure, name='razorpay_payment_failure'),
    path('wallet/transactions/', views.wallet_transactions, name='wallet_transactions'),

  

    path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),

    #test
 
    path('submit-return/<int:item_id>/', views.submit_return, name='submit_return'),
    path('cancel-item/<int:item_id>/', views.cancel_item, name='cancel_item'),



]

# Static files (images, CSS, JavaScript, etc.) 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
