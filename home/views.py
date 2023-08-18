from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from .decorators import admin_login_required
from django.shortcuts import get_object_or_404, redirect, render
from home.forms import (CouponForm, EditUserForm, LaptopForm,
                        MobileForm, ProductForm, ProfileForm, ShippingAddressForm,
                        UserAuthenticationForm, UserSignupForm)
from home.models import (Cart, CartItem, Contact, Coupon, Laptop, Mobile,
                         Order, OrderItem, Product, Profile,ShippingAddress)
import paypalrestsdk 
from django.http import QueryDict
from django.template.loader import render_to_string
# customer site views

#home page
def home(request):
    products = Product.get_products()
    return render(request, 'customer/home.html', context={'products': products})

#cart view
@login_required()
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    cart.total = cart.get_cart_total()
    cart.save()
    coupon_form = CouponForm()
    coupons = Coupon.objects.all()
    return render(request, 'customer/cart.html', {'cart_items': items, 'cart': cart, 'coupons':coupons, 'coupon_form': coupon_form})


#adding products to cart
@login_required()
def add_to_cart(request, product_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, pk = product_id)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        item.quantity += 1
        cart.total = cart.get_cart_total()
        messages.success(request, 'Cart Updated.')
        item.save()
    messages.success(request, 'Added to cart.')
    return redirect('cart')


# increase quantity of product
def increase_cart_item_quantity(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')


# decrease quantity of product
def decrease_cart_item_quantity(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    if not cart.items() and cart.coupon_use:
        cart.coupon_use.used -= 1
        cart.coupon_use=None
        cart.save()
    return redirect('cart')


# delete product from cart
def remove_cart_item(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product_id)
    cart_item.delete()
    if not cart.items() and cart.coupon_use:
        cart.coupon_use.used -= 1
        cart.coupon_use = None
        cart.save()
    return redirect('cart')


#applying coupon
def apply_coupon(request,code):
  cart = get_object_or_404(Cart, user=request.user)
  if not cart:
        cart = Cart.objects.create(user=request.user)
  coupon_form = CouponForm(request.POST)
  if coupon_form.is_valid():
      code = coupon_form.cleaned_data['code']
  if code:
    try:
        coupon = get_object_or_404(Coupon, code = code)
    except Coupon.DoesNotExist:
        messages.error(request, 'Invalid coupon code.')
        return redirect('cart')
    if cart.apply_coupon(coupon):
        messages.success(request, 'Coupon applied.')
    else:
        messages.error(request, 'Coupon usage limit reached.')
  else:
      messages.error(request, 'Invalid coupon code.')
  return redirect('cart')


def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    shipping_address = ShippingAddress.objects.filter(cart=cart, user=request.user).first()
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.cart = cart
            shipping_address.save()
            form = ShippingAddressForm(instance=shipping_address)  # Update form with saved data
    else:
        form = ShippingAddressForm()

    cart_items = cart.items()

    return render(request, 'customer/checkout.html', context={
        'cart': cart,
        'form': form,
        'cart_items': cart_items,
        'shipping_address': shipping_address,
    })

# update the order status if payment is successful
def update_order_status(request):
    if request.method == 'POST':
        cart_id = request.POST.get('cart_id')
        billing_address = request.POST.get('billing_address')
        cart = get_object_or_404(Cart, pk=cart_id)
        if cart and cart.items():
            # Create order and order items if the order is placed successfully
            shipping_address = get_object_or_404(ShippingAddress,user=request.user, cart=cart)
            if not billing_address:
                billing_address=shipping_address
            concatenated_address = f'{shipping_address.address_line1}, {shipping_address.address_line2}, {shipping_address.city}, {shipping_address.state}, {shipping_address.pin_code}'
            order = Order.objects.create(user=request.user, total=cart.total, discount_amount=cart.discount_amount, coupon_use=cart.coupon_use, billing_address=billing_address ,shipping_address=concatenated_address)
    
            for cart_item in cart.items():
                order_item, _ = OrderItem.objects.get_or_create(
                    order=order, product=cart_item.product, quantity=cart_item.quantity, price=cart_item.product.price)
            # Delete cart items
            CartItem.objects.filter(cart=cart).delete()

            response_data = {'success': True, 'message': 'Order Placed successfully.'}
        else:
            response_data = {'success': False, 'message': 'Cart is empty.'}
    else:
        response_data = {'success': False, 'message': 'Invalid request method.'}

    return JsonResponse(response_data)


#order history of user
@login_required
def customer_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'customer/your_orders.html', context)


#detail order view for past orders
@login_required
def view_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'customer/view_order.html', {'order': order, 'order_items': order_items})


#about page
def about(request):
    return render(request, 'customer/about.html')


#contact page
def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        msg = request.POST['msg']
        contact = Contact(user=request.user,name=name, email=email, phone=phone, msg=msg)
        contact.save()
    return render(request, 'customer/contact.html')



#product admin site 

#dashboard for admin
@admin_login_required
def product_admin(request):
    return render(request, 'admin/product_admin.html')


# adding products on admin site
@admin_login_required
def add_products(request):
    category = request.POST.get('category-input')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.product_admin = request.user
            product.category = category
            product.save()

            if category == 'Mobile':
                detail_form = MobileForm(request.POST)
            elif category == 'Laptop':
                detail_form = LaptopForm(request.POST)
            if detail_form.is_valid():
                detail_product = detail_form.save(commit=False)
                detail_product.product = product
                detail_product.save()
            messages.success(request, 'Product added')
            return redirect("view_products")
        else:
            if category == 'Mobile':
                form = ProductForm()
                detail_form = MobileForm()
            else:
                form = ProductForm()
                detail_form = LaptopForm()
    else:
        category = ''
        form = detail_form = None

    return render(request, 'admin/add_products.html', {'form': form, 'detail_form': detail_form, 'category': category})


# products display entered by admin
@admin_login_required
def view_products(request):
    product_admin = request.user
    products = Product.get_products_by_admin(product_admin=product_admin)
    return render(request, 'admin/view_products.html', context={'products': products})


# detail product view
@login_required()
def detail_product_view(request, product_id):
    if request.user.user_type == "Admin":
        base_template = 'admin/admin_base.html'
    else:
        base_template = 'customer/base.html'
    product = get_object_or_404(Product, pk = product_id)
    if product.category == "Mobile":
        detail_product = get_object_or_404(Mobile, product=product)
    else:
        detail_product = get_object_or_404(Laptop, product=product)

    return render(request, "product_detail.html", {'detail_product': detail_product, 'base_template': base_template, 'user': request.user.user_type})


# edit product detail
@admin_login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = ProductForm(instance=product)
    if product.category == "Mobile":
        detail_product = get_object_or_404(Mobile, product=product)
        detail_form = MobileForm(instance=detail_product)

    else:
        detail_product = get_object_or_404(Laptop, product=product)
        detail_form = LaptopForm(instance=detail_product)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES,
                           instance=product)
        if product.category == "Mobile":
            detail_form = MobileForm(
                request.POST, request.FILES, instance=detail_product)

        else:
            detail_form = LaptopForm(request.POST, request.FILES,
                                     instance=detail_product)
        if form.is_valid():
            form.save()
            detail_form.save()
            messages.success(request, "Product is updated.")
            return redirect('view_products')
        else:
            form = ProductForm(instance=product)
    return render(request, "admin/edit_product.html", {'form': form, 'detail_form': detail_form, 'detail_product': detail_product})


# delete product
@admin_login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if product.category == "Mobile":
        detail_product = get_object_or_404(Mobile, product=product)
    else:
        detail_product = get_object_or_404(Laptop, product=product)
    product.delete()
    detail_product.delete()
    messages.success(request, "Product is deleted.")
    return redirect("view_products")


#to display the orders
@admin_login_required
def orders(request):
  orders = Order.objects.all()
  placed_orders=[]
  for order in orders:
        placed_orders += OrderItem.objects.filter(order=order, product__product_admin=request.user)
  context = {'orders': placed_orders}
  return render(request, 'admin/orders.html', context)


#user account creation
def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            messages.success(request, f'Your account has been created.')
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
            if user is not None:
                if not user.is_approved and user.user_type=="Admin":
                    messages.error(
                        request, 'Your account is still waiting for admin approval.')
                    redirect("login")
                else: 
                    login(request, user)
                    messages.info(
                        request, f"You are now logged in as @{username}.")
                    if user.user_type == 'Customer':
                        return redirect("home") 
                    else:
                        return redirect("product_admin")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = UserAuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form": form})


#user logout
@login_required()
def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    if request.user == "Customer":
        return redirect("home")
    else:
        return redirect("login")


#to display the profile details
@login_required()
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.user.user_type == "Admin":
        base_template = 'admin/admin_base.html'
    else:
        base_template = 'customer/base.html'
    return render(request, "profile.html", context={"profile": profile, "base_template": base_template})


#to edit the profile details
@login_required()
def edit_profile(request):
    if request.user.user_type == "Admin":
        base_template = 'admin/admin_base.html'
    else:
        base_template = 'customer/base.html'

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid() and profile_form.is_valid():
            user_form = form.save()
            custom_form = profile_form.save(False)
            custom_form.user = user_form
            custom_form.save()
            return redirect('profile')
    else:
        form = EditUserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        context = {"form": form, "profile_form": profile_form,
                   "base_template": base_template}
        return render(request, 'edit_profile.html', context=context)
