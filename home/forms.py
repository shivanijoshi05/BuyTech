from django import forms
from django.contrib.auth.forms import UserCreationForm
from home.models import CustomUser, Laptop, Mobile, Product, Profile


# To create user signup detail form
USER_TYPE = (
    ('Admin', 'Admin'),
    ('Customer', 'Customer')
)


class UserSignupForm(UserCreationForm):
    is_product_admin = forms.CharField(
        label="", widget=forms.RadioSelect(choices=USER_TYPE))
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Username'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Email'}))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Password'}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Confirm password'}))

    class Meta:
        model = CustomUser
        fields = ['is_product_admin', 'username',
                  'email', 'password1', 'password2']

        def clean(self):
            super(UserSignupForm, self).clean()
            return self.cleaned_data


# To create user login details form
class UserAuthenticationForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Password'}))


# To create product detail form
CATEGORY = (
    ('Mobile', 'Mobile'),
    ('Laptop', 'Laptop')
)


class ProductForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Product Name'}))
    price = forms.IntegerField(widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Price'}))
    description = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter description'}))
    image = forms.FileField()

    class Meta:
        model = Product
        exclude = ['product_admin', 'category']
        fields = ['name', 'price', 'description', 'image']


# To create Mobile detail form
class MobileForm(forms.ModelForm):
    BRAND_CHOICES = [
        ('Apple', 'Apple'),
        ('Samsung', 'Samsung'),
        ('OnePlus', 'OnePlus'),
        ('Xiaomi', 'Xiaomi'),
        ('Google', 'Google'),
    ]
    brand = forms.CharField(
        label="Brands", widget=forms.RadioSelect(choices=BRAND_CHOICES))
    screen_size = forms.CharField(label="Screen Size", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter screen size'}))
    os = forms.CharField(label="Operating System", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Operating System'}))
    battery = forms.CharField(label="Battery", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Battery power'}))
    color = forms.CharField(label="Color", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Color'}))

    class Meta:
        model = Mobile
        exclude = ['product']
        fields = ('brand', 'screen_size', 'os', 'battery', 'color')


# To create Laptop detail form
class LaptopForm(forms.ModelForm):
    BRAND_CHOICES = [
        ('Apple', 'Apple'),
        ('Dell', 'Dell'),
        ('Lenovo', 'Lenovo'),
        ('HP', 'HP'),
        ('Acer', 'Acer'),
    ]
    brand = forms.CharField(
        label="Brands", widget=forms.RadioSelect(choices=BRAND_CHOICES))
    screen_size = forms.CharField(label="Screen Size", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter screen size'}))
    processor = forms.CharField(label="Processor", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter processor name'}))
    ram = forms.CharField(label="RAM", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter RAM'}))
    storage = forms.CharField(label="Storage", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Storage'}))
    color = forms.CharField(label="Color", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Color'}))

    class Meta:
        model = Laptop
        exclude = ['product']
        fields = ('brand', 'screen_size', 'processor',
                  'ram', 'storage', 'color')

# To edit user signup detail form
class EditUserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter username'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter email'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


# To create user profile detail form
class ProfileForm(forms.ModelForm):
    profile_img = forms.FileField()
    mobile = forms.CharField(widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Mobile'}))
    bio = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Bio'}))
    address = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Address'}))

    class Meta:
        model = Profile
        fields = ('profile_img', 'mobile', 'bio', 'address')


# To create user checkout detail form
class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(max_length=255)
    name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()

#to get coupon details
class CouponForm(forms.Form):
    code = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter coupon code'
    }))
