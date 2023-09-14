from django.contrib import admin

from .models import Laptop, Mobile, Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'product_admin')
    list_filter = ('category',)
    search_fields = ('name',)

class MobileAdmin(admin.ModelAdmin):
    list_display = ('product', 'brand', 'screen_size', 'os', 'battery', 'color')
    list_filter = ('brand', 'color')
    search_fields = ('product__name',)

class LaptopAdmin(admin.ModelAdmin):
    list_display = ('product', 'brand', 'screen_size', 'processor', 'ram', 'storage', 'color')
    list_filter = ('brand', 'color')
    search_fields = ('product__name',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Mobile, MobileAdmin)
admin.site.register(Laptop, LaptopAdmin)
