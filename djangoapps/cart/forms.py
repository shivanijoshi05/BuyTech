# To create user checkout detail form
from .models import ShippingAddress
from django import forms


class ShippingAddressForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Name'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}
    ))
    address_line1 = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}
    ))
    address_line2 = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Address Line 2'}
    ))
    pin_code = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Pin Code'}
    ))
    city = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'City/Town'}))
    state = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'State'}))
    country = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Country'}))
    
    class Meta:
        model = ShippingAddress
        fields = [
            'name', 'email', 'address_line1', 'address_line2',
            'pin_code', 'city', 'state', 'country'
        ]


