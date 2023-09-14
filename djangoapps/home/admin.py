from django.contrib import admin
from .models import Contact, Coupon, CouponUse

class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'phone', 'msg')
    list_filter = ('user', 'name', 'email')
    search_fields = ('user__username', 'name', 'email', 'phone', 'msg')

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount', 'usage_limit')
    list_filter = ('discount_type',)
    search_fields = ('code', 'discount_type')

class CouponUseAdmin(admin.ModelAdmin):
    list_display = ('user', 'coupon', 'used')
    list_filter = ('user', 'coupon')
    search_fields = ('user__username', 'coupon__code')

# Register the custom admin classes for your models
admin.site.register(Contact, ContactAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(CouponUse, CouponUseAdmin)
