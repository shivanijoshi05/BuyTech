from django import forms
from .models import Laptop, Mobile, Product

CATEGORY = (
    ('Mobile', 'Mobile'),
    ('Laptop', 'Laptop')
)

# To create product detail form
class ProductForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter product name'}))
    price = forms.IntegerField(widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter price'}))
    stock = forms.IntegerField(widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter product stock quantity'}))
    description = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter description'}))
    image = forms.FileField()

    class Meta:
        model = Product
        exclude = ['product_admin', 'category']
        fields = ['name', 'price', 'stock', 'description', 'image']


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
        attrs={'class': 'form-control', 'placeholder': 'Enter operating system'}))
    battery = forms.CharField(label="Battery", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter battery power'}))
    color = forms.CharField(label="Color", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter color'}))

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
        attrs={'class': 'form-control', 'placeholder': 'Enter storage'}))
    color = forms.CharField(label="Color", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter color'}))

    class Meta:
        model = Laptop
        exclude = ['product']
        fields = ('brand', 'screen_size', 'processor', 'ram', 'storage', 'color')

