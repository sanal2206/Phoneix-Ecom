from django.urls import path, include
from store_manager import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import  admin_dashboard, logout_user,AdminLoginView

urlpatterns = [
 

    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('logout/', logout_user, name='admin_logout'),

    #adding items
    path('add/product', views.add_product, name='add_product'),
    path('add/colour', views.add_color, name='add_color'),
    path('add/variant', views.add_variant, name='add_variant'),
    path('add/storage', views.add_storage, name='add_storage'),
    path('add/brand',views.add_brand,name='add_brand'),
    path('delete/brand/<int:id>',views.delete_brand,name='delete_brand'),
    path('add/coupon',views.add_coupon,name='add_coupon'),
    path('couponlist',views.coupon_list,name='coupon_list'),
    path('delete/coupon/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),

    path('delete/colour/<int:id>',views.delete_colour,name='delete_colour'),


    #typeCategory

    path('typecategorylist',views.typecategory_list,name='typecategory_list'),
    path('add/typecategory',views.add_typecategory,name='add_typecategory'),
    path('typecategory/<int:id>/toggle-status/', views.toggle_typecategory_status, name='toggle_typecategory_status'),
    path('typecategory/<int:id>/edit/', views.edit_typecategory, name='edit_typecategory'),
    path('typecategory/<int:id>/delete/', views.delete_typecategory, name='delete_typecategory'),


         
    #edit
    path('edit/product/<int:product_id>/', views.edit_product, name='admin_edit_product'),
    path('edit_variant/<int:variant_id>/', views.edit_variant, name='edit_variant'),
    path('delete_variant/<int:variant_id>/',views.delete_variant,name='delete_variant'),
 

    path('category/deactivate/<int:category_id>/', views.deactivate_category, name='deactivate_category'),
    path('category/activate/<int:category_id>/', views.activate_category, name='activate_category'),

     path('orders/', views.store_manager_orders, name='store_manager_orders'),
     path('store-manager/orders/<int:order_id>/', views.store_manager_order_detail, name='store_manager_order_detail'),


    #deactivate
    path('deactivate/product/<int:product_id>/', views.deactivate_product, name='admin_deactivate_product'),

    path('productlist/<int:product_id>/', views.product_list, name='product_list'),  # Accepts a product_id
    path('deactivate/variant/<int:variant_id>/', views.deactivate_variant, name='admin_deactivate_variant'),

    path('product/<int:pk>/delete/', views.soft_delete_product, name='soft_delete_product'),  # Soft delete product
     path('product/<int:pk>/', views.Product_detail, name='product_detail'),  # Update accordingly



     #deleted_products
     path('deleted-products/', views.deleted_product_list, name='deleted_product_list'),
    path('restore-product/<int:product_id>/', views.restore_product, name='restore_product'),
    path('delete-product-permanently/<int:product_id>/', views.permanent_delete_product, name='permanent_delete_product'),
    
    
    
    #list of items
    path('productlist/', views.product_list, name='product_list'),
    path('colorlist/', views.color_list, name='color_list'),
    path('variantlist/', views.variant_list, name='variant_list'),
    path('categorylist/',views.category_list,name='category_list'),
    path('brandlist/',views.brand_list,name='brand_list'),


    path('storage_list/', views.storage_list, name='storage_list'),
    path('deactivate_storage/<int:storage_id>/', views.deactivate_storage, name='deactivate_storage'),
    path('activate_storage/<int:storage_id>/', views.activate_storage, name='activate_storage'),

     #user managment
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/toggle/<int:user_id>/', views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('admin/users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),

#     # Password reset URLs (for admin password reset)
#     path('password-reset/', 
#          auth_views.PasswordResetView.as_view(template_name='admin_password_reset.html'), 
#          name='admin_password_reset'),

#     path('reset/<uidb64>/<token>/', 
#          auth_views.PasswordResetConfirmView.as_view(template_name='admin_password_reset_confirm.html'), 
#          name='password_reset_confirm'),

#     path('reset/done/', 
#          auth_views.PasswordResetCompleteView.as_view(template_name='admin_password_reset_complete.html'), 
#          name='password_reset_complete'),

#     path('password-reset/done/', 
#          auth_views.PasswordResetDoneView.as_view(template_name='admin_password_reset_done.html'), 
#          name='password_reset_done'),

    # Include the URLs for allauth (if you're using it for authentication)


    path('sales_report/<str:report_type>/', views.generate_sales_report, name='generate_sales_report'),
    path('sales_report.html/', views.generate_sales_report, name='generate_sales_report'),

    path('manage-return-requests/', views.manage_return_requests, name='manage_return_requests'),
    path('update-return-request/<int:return_request_id>/', views.update_return_request, name='update_return_request'),


    path('accounts/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
