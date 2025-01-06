from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import OtpToken,CustomUser,Wallet 
from django.core.mail import send_mail
from django.utils import timezone
from allauth.socialaccount.models import SocialAccount
 
 
@receiver(post_save, sender=settings.AUTH_USER_MODEL) 
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            pass
        
        else:

            if SocialAccount.objects.filter(user=instance).exists():
                # Skip OTP generation for users using social accounts
                return
            

            OtpToken.objects.create(user=instance, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
            instance.is_active=False 
            instance.save()
        
        
        # email credentials
        otp = OtpToken.objects.filter(user=instance).last()
       
       
        subject="Email Verification"
        message = f"""
                                Hi {instance.username}, here is your OTP {otp.otp_code} 
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/verify-email/{instance.username}
                                
                                """
        sender = "sanalsabu22@gmail.com"
        receiver = [instance.email, ]
       
        
        
        # send email
        send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False,
            )
  

from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(social_account_added)
def activate_social_user(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    if not user.is_active:  # Only update if the user is inactive
        user.is_active = True
        user.verification_method = sociallogin.account.provider.capitalize()
        user.save()  
 

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User 
from .models import Coupon, UserCoupon
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta

from django.contrib.auth import get_user_model
from .models import Coupon
 
 


User = get_user_model()

@receiver(post_save, sender=User)
def give_coupon_on_registration(sender, instance, created, **kwargs):
    if created:
        # Check if the user already has a coupon (not necessary for new users, but good practice)
        existing_coupons = UserCoupon.objects.filter(user=instance, is_used=False)
        if not existing_coupons.exists():
            # Create a new coupon
            coupon = Coupon.objects.create(
                code=f"WELCOME{instance.id}",  # Generate a unique code
                discount_percent=10,  # Example discount percentage
                start_date=now(),
                end_date=now() + timedelta(days=30),  # Valid for 30 days
                usage_limit=1,
                usage_count=0,
                
            )
            # Assign the coupon to the user
            UserCoupon.objects.create(user=instance, coupon=coupon, is_used=False)
