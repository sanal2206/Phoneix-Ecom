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



@receiver(post_save, sender=Coupon)
def assign_coupon_to_users_on_creation(sender, instance, created, **kwargs):
    """
    Automatically assigns a newly created coupon to all users.
    """
    if created:  # Trigger only when a new coupon is created
        users = User.objects.all()  # Fetch all users
        user_coupons = []

        for user in users:
            # Avoid duplicate assignments
            if not UserCoupon.objects.filter(user=user, coupon=instance).exists():
                user_coupons.append(UserCoupon(user=user, coupon=instance))

        # Bulk create to optimize database performance
        UserCoupon.objects.bulk_create(user_coupons)
        print(f"Coupon '{instance.code}' assigned to all users.")

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Wallet, WalletTransaction

@receiver(post_save, sender=Order)
def refund_wallet(sender, instance, **kwargs):
    if instance.status in ['Cancelled', 'Returned'] and instance.payment_status == 'Paid':
        refund_amount = instance.wallet_amount_used + instance.total_price
        instance.user.wallet.add_funds(refund_amount)
        WalletTransaction.objects.create(
            user=instance.user,
            amount=refund_amount,
            transaction_type='Refund',
            description=f"Refund for {instance.status.lower()} order {instance.id}"
        )


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Wallet

User = get_user_model()

@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)


from django.dispatch import Signal

# Define a signal for the return request approval
return_request_approved = Signal()

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ReturnRequest, WalletTransaction

@receiver(post_save, sender=ReturnRequest)
def handle_refund(sender, instance, created, **kwargs):
    if not created and instance.status == 'Approved':
        # Process refund
        try:
            order_item = instance.order_item
            order = order_item.order

            # Calculate refund amount
            refund_amount = order_item.total_cost * order_item.quantity

            # Check payment status
            if order.payment_status == 'Paid':
                # Full refund for paid orders
                wallet = instance.user.wallet
                wallet.add_funds(refund_amount)
                WalletTransaction.objects.create(
                    user=instance.user,
                    amount=refund_amount,
                    transaction_type='Refund',
                    description=f"Refund approved for return request of order item {instance.order_item.id}"
                )
            elif order.payment_method == 'COD' and order.wallet_amount_used > 0:
                # If COD, refund only the wallet amount used
                wallet = instance.user.wallet
                wallet.add_funds(order.wallet_amount_used)
                
                WalletTransaction.objects.create(
                    user=instance.user,
                    amount=order.wallet_amount_used,
                    transaction_type='Refund',
                    description=f"Wallet refund approved for return request of order item {instance.order_item.id}"
                )
        except Exception as e:
            print("Error during refund processing:", e)

