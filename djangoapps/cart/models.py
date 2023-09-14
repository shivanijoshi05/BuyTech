

from django.db import models, transaction
from djangoapps.home.models import CouponUse
from djangoapps.product.models import Product
from djangoapps.user_account.models import CustomUser


#to store cart items 
class Cart(models.Model):
    """
    A Cart model to store cart items, and related functions to manage 
    the cart such as applying or removing coupons, calculating the total cost of 
    the cart, and getting the list of cart items.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon_use = models.ForeignKey(
        CouponUse, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def items(self):
        return CartItem.objects.filter(cart=self)

    def apply_coupon(self, coupon):
        if coupon:
            coupon_use, created = CouponUse.objects.get_or_create(user=self.user, coupon=coupon)
            if coupon_use.used < coupon.usage_limit:
                try:
                    with transaction.atomic():
                        coupon_use.save()
                        self.coupon_use = coupon_use
                        self.discount_amount = coupon.calculate_discounted_total(self.total)
                        self.save()
                    return True
                except Exception as e:
                    pass
        return False

    def save_coupon_use(self):
        if coupon_use := self.coupon_use:
            coupon_use.used += 1
            coupon_use.save()
        self.coupon_use = None
        self.discount_amount = 0
        self.save()

    def get_cart_total(self):
        self.total = sum(item.get_total() for item in self.items())
        if self.coupon_use:
            if self.total > 0:
                self.discount_amount = self.coupon_use.coupon.calculate_discounted_total(self.total)
                
            else:
                self.discount_amount = 0
        else:
            self.discount_amount = self.total
        self.save()
        return self.total
    
    def get_discount(self):
        if self.coupon_use:
            return self.coupon_use.coupon.calculate_coupon_discount(self.total)
        return 0.00
        

# to store the cart items details
class CartItem(models.Model):
    """
    A model to store the details of a product added to a cart.
    """
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total(self):
        return self.product.price * self.quantity


# to store the shipping address
class ShippingAddress(models.Model):
    """
    A ShippingAddress model represents a shipping address of an order.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    user =  models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    email = models.EmailField('email')
    address_line1 = models.CharField(max_length=60)
    address_line2 = models.CharField(max_length=60)
    pin_code = models.CharField(max_length=6)
    city = models.CharField(max_length=60)
    state = models.CharField(max_length=60)
    country = models.CharField(max_length=60)
    
    def __str__(self):
        return f"Shipping Address of {self.user.username} for order - {self.cart.id}"