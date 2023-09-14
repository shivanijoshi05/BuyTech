from django.db import models
from djangoapps.home.models import CouponUse
from djangoapps.product.models import Product
from djangoapps.user_account.models import CustomUser

STATUS_CHOICES = (
    ("Placed", "Placed"),
    ("Processing", "Processing"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
)

# to store user orders
class Order(models.Model):
    """
    A Order model represents a user's order with their purchased items.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_use = models.ForeignKey(
        CouponUse, on_delete=models.SET_NULL, null=True, blank=True
    )
    billing_address = models.CharField(max_length=150, default="")
    shipping_address = models.CharField(max_length=150, default="")

    def __str__(self):
        return f"Order {self.id}"

    def placeOrder(self):
        self.save()


# to store the order item details
class OrderItem(models.Model):
    """
    A OrderItem model represents an item purchased in an order.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Placed")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total(self):
        return self.price * self.quantity

    @staticmethod
    def calculate_order_items_total(order_items):
        return sum(item.get_total() for item in order_items)
