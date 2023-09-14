from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser, Profile


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


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_img', 'mobile', 'bio', 'address')
    search_fields = ('user__username', 'user__email')
    list_filter = ('mobile',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)