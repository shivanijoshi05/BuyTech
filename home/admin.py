from django.contrib import admin
from home.models import Cart, CartItem, Coupon, CustomUser,Contact, Laptop, Mobile, Order, Product, Profile

# to display models on admin site
admin.site.register(CustomUser)
admin.site.register(Contact)
admin.site.register(Product)
admin.site.register(Mobile)
admin.site.register(Laptop)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Coupon)
admin.site.register(CartItem)
