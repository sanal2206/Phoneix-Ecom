from decimal import Decimal
from django.utils.timezone import now
from .models import UserCoupon
import razorpay
from django.conf import settings
from .models import Offer

def calculate_totals(cart_items, coupon_id=None, user=None):
    subtotal = sum(Decimal(item.variant.price) * item.quantity for item in cart_items)
    discount_total = sum(
        (Decimal(item.variant.price) * (Decimal(item.variant.product.discount) / 100)) * item.quantity
        for item in cart_items if item.variant.product.discount > 0
    )


     # Add type_category offers to the discount total
    for item in cart_items:
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

    coupon_discount = Decimal('0.00')
    applied_coupon = None

    if coupon_id and user:
        try:
            user_coupon = UserCoupon.objects.get(user=user, coupon_id=coupon_id, is_used=False)
            coupon = user_coupon.coupon
            current_time = now()
            if (coupon.start_date <= current_time <= coupon.end_date and
                coupon.usage_count < coupon.usage_limit and
                coupon.is_active):

                applied_coupon = coupon
                discountable_amount = subtotal - discount_total
                coupon_discount = (discountable_amount * Decimal(coupon.discount_percent) / 100)
            else:
                raise UserCoupon.DoesNotExist
        except UserCoupon.DoesNotExist:
            applied_coupon = None

    shipping_cost = Decimal('5.00')
    total = subtotal - discount_total - coupon_discount + shipping_cost

    return subtotal, discount_total, coupon_discount, applied_coupon, shipping_cost, total

 
import razorpay
from django.conf import settings

def create_razorpay_order(amount, currency='INR'):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    data = {
        'amount': amount,  # Amount is already in paise
        'currency': currency,
        'payment_capture': 1  # Capture the payment automatically
    }
    return client.order.create(data=data)
