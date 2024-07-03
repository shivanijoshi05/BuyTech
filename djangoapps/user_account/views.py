from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EditUserForm, ProfileForm, UserAuthenticationForm, UserSignupForm
from .models import Profile


#user account creation
def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            messages.success(request, 'Your account has been created.')
            user = authenticate(username=username, password=password)
            if user is not None:
                if not user.is_approved and user.user_type=="Admin":
                    messages.error(
                        request, 'Your account is still waiting for admin approval.')
                    return redirect("login")
                else:
                    login(request, user)
                    messages.info(
                        request, f"You are now logged in as @{username}.")
                    if user.user_type == 'Customer':
                        return redirect("home")
                    else:
                        return redirect("product_admin")
    else:
        form = UserSignupForm()
    context = {'form': form}
    return render(request, 'signup.html', context)


#user login
def user_login(request):
    if request.method == "POST":
        form = UserAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is None:
                messages.error(request, "Invalid username or password.")
            elif not user.is_approved and user.user_type=="Admin":
                messages.error(
                    request, 'Your account is still waiting for admin approval.')
                redirect("login")
            else: 
                login(request, user)
                messages.info(
                    request, f"You are now logged in as @{username}.")
                return (
                    redirect("home")
                    if user.user_type == 'Customer'
                    else redirect("product_admin")
                )
        else:
            messages.error(request, "Invalid username or password.")
    form = UserAuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form": form})


#user logout
@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("login")
    
#to display the profile details
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.user.user_type == "Admin":
        base_template = 'admin/admin_base.html'
    else:
        base_template = 'customer/base.html'
    return render(request, "profile.html", context={"profile": profile, "base_template": base_template})


#to edit the profile details
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.user_profile)
        if form.is_valid() and profile_form.is_valid():
            user_form = form.save()
            custom_form = profile_form.save(False)
            custom_form.user = user_form
            custom_form.save()
            return redirect('profile')
    else:
        form = EditUserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.user_profile)
        base_template = ('admin/admin_base.html' if request.user.user_type == "Admin" else 'customer/base.html')
        context = {"form": form, "profile_form": profile_form, "base_template": base_template}
        return render(request, 'edit_profile.html', context=context)
