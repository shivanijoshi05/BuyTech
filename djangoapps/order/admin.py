from django.contrib import admin
from .models import Order, OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total', 'created_at', 'discount_amount', 'coupon_use')
    list_filter = ('user', 'created_at', 'coupon_use')
    search_fields = ('user__username', 'coupon_use__coupon__code')

    ordering = ('-created_at',)

    readonly_fields = ('total', 'created_at', 'discount_amount', 'billing_address', 'shipping_address')


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'status')
    list_filter = ('status',)
    actions = ['set_status_processing', 'set_status_shipped', 'set_status_delivered']

    def set_status_processing(self, request, queryset):
        queryset.update(status='processing')

    def set_status_shipped(self, request, queryset):
        queryset.update(status='shipped')

    def set_status_delivered(self, request, queryset):
        queryset.update(status='delivered')

    set_status_processing.short_description = "Set selected items as Processing"
    set_status_shipped.short_description = "Set selected items as Shipped"
    set_status_delivered.short_description = "Set selected items as Delivered"

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
