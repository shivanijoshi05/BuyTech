from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser, Profile

USER_TYPE = (
    ('Admin', 'Admin'),
    ('Customer', 'Customer')
)

# To create user signup detail form
class UserSignupForm(UserCreationForm):
    user_type = forms.CharField(
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
        fields = ['user_type', 'username',
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