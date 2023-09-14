from django.contrib import admin

from .models import Cart, CartItem, ShippingAddress


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total', 'discount_amount', 'coupon_use')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username',)
    inlines = [CartItemInline]

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'get_total')
    list_filter = ('cart__user', 'product__category')
    search_fields = ('cart__user__username', 'product__name')
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total Cost'

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('cart', 'user', 'name', 'email', 'city', 'state')
    list_filter = ('cart__user', 'city', 'state', 'country')
    search_fields = ('cart__user__username', 'name', 'email')

# Register the custom admin classes for your models
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
