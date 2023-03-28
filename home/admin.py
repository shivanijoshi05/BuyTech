from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from home.models import (Cart, CartItem, Contact, Coupon, CustomUser, Laptop,
                         Mobile, Order, OrderItem, Product, Profile)


class CustomUserAdminForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
        exclude = ['password']


class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom fields', {'fields': ('user_type', 'is_approved')})
    )

    list_display = ('username', 'email', 'user_type',
                    'is_approved', 'is_staff', 'is_superuser')
    list_filter = ('user_type', 'is_approved', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_display = ('username', 'email', 'user_type', 'is_approved')


admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Contact)
admin.site.register(Product)
admin.site.register(Mobile)
admin.site.register(Laptop)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Coupon)
admin.site.register(CartItem)
admin.site.register(OrderItem)
