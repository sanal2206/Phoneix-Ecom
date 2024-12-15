from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('login/',views.login_user,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('register/',views.register_user,name='register'),
    path("verify-email/<slug:username>", views.verify_email, name="verify-email"),
    path("resend-otp", views.resend_otp, name="resend-otp"),
    path('product/<int:pk>',views.product,name='product'),
    path('category/<str:cat>',views.category,name='category'),

    #Profile
    path('profile/', views.user_profile, name='user_profile'),
    path('add-address/', views.add_address, name='add_address'),
     path('manage-address/', views.manage_address, name='add_address'),
     path('manage-address/<int:address_id>/', views.manage_address, name='edit_address'),
     path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('update-profile/', views.update_profile, name='update_profile'),

      
    #passoword reset
     
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'), 
         name='password_reset'),
 
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),
     path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),

     # path('accounts/', include('allauth.urls')),

     
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
