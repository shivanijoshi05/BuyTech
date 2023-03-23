from datetime import timezone
from django.shortcuts import get_object_or_404, render, redirect
from home import models
from home.forms import CheckoutForm, CouponForm, EditUserForm, LaptopForm, MobileForm, ProductForm, ProfileForm, UserSignupForm, UserAuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from home.models import Cart, CartItem, Contact, Coupon, CustomUser, Laptop, Mobile, Order, OrderItem, Product, Profile
from django.contrib.auth.decorators import login_required


# customer site views

#home page
def home(request):
    return render(request, 'customer/home.html')


#products display
def products(request):
    products = Product.get_products()
    return render(request, 'customer/products.html', context={'products': products})


#cart view
@login_required()
def cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        cart = Cart.objects.create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    cart.total = cart.get_cart_total()
    cart.save()
    coupon_form = CouponForm()
    coupons = Coupon.objects.all()
    return render(request, 'customer/cart.html', {'cart_items': items, 'cart': cart, 'coupons':coupons, 'coupon_form': coupon_form})


#adding products to cart
@login_required()
def add_to_cart(request, product_id):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        cart = Cart.objects.create(user=request.user)
    product = Product.objects.filter(id=product_id).first()
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
    cart = Cart.objects.filter(user=request.user).first()
    cart_item = get_object_or_404(CartItem, cart=cart,product=product_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')


# decrease quantity of product
def decrease_cart_item_quantity(request, product_id):
    cart = Cart.objects.filter(user=request.user).first()
    cart_item = get_object_or_404(CartItem, cart=cart, product=product_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    if not cart.items():
        cart.coupon_use.used -= 1
        cart.coupon_use=None
        cart.save()
    return redirect('cart')


# delete product from cart
def remove_cart_item(request, product_id):
    cart = Cart.objects.filter(user=request.user).first()
    cart_item = get_object_or_404(CartItem, cart=cart, product=product_id)
    cart_item.delete()
    if not cart.items():
        cart.coupon_use.used -= 1
        cart.coupon_use = None
        cart.save()
    return redirect('cart')


#applying coupon
def apply_coupon(request,code):
  cart = Cart.objects.filter(user=request.user).first()
  if not cart:
        cart = Cart.objects.create(user=request.user)
  coupon_form = CouponForm(request.POST)
  if coupon_form.is_valid():
      code = coupon_form.cleaned_data['code']
  if code:
    try:
        coupon = Coupon.objects.get(code=code)
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


#checkout and place order
def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cart = Cart.objects.get(user=request.user)
            if not cart:
                messages.error(request, 'Your cart is empty.')
                return redirect('cart')
            order = Order.objects.create(
                user=request.user, total=cart.total, discount_amount=cart.discount_amount, coupon_use=cart.coupon_use)
            cart.remove_coupon()
            for item in cart.items():
                OrderItem.objects.create(
                    order=order, product=item.product, quantity=item.quantity, price=item.product.price)
            CartItem.objects.filter(cart=cart).delete()
            messages.success(request, 'Your order has been placed.')
            return redirect('your_orders')
    else:
        form = CheckoutForm()
    context = {
        'form': form,
    }
    return render(request, 'customer/checkout.html', context)


#order history of user
@login_required
def customer_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders
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
        contact = Contact(name=name, email=email, phone=phone, msg=msg)
        contact.save()
    return render(request, 'customer/contact.html')



#product admin site 

#dashboard for admin
def product_admin(request):
    return render(request, 'admin/product_admin.html')


# adding products on admin site
@login_required()
def add_products(request):
    category = request.POST.get('category-input')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            product = form.save(commit=False)
            product.product_admin = request.user
            product.category = category
            product.save()

            print(product)
            if category == 'Mobile':
                detail_form = MobileForm(request.POST)
                print(detail_form)
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
@login_required()
def view_products(request):
    product_admin = request.user
    products = Product.get_products_by_admin(product_admin=product_admin)
    return render(request, 'admin/view_products.html', context={'products': products})


# detail product view
@login_required()
def detail_product_view(request, product_id):
    if request.user.is_product_admin == "Admin":
        base_template = 'admin/admin_base.html'
    else:
        base_template = 'customer/base.html'
    product = Product.objects.filter(id=product_id).first()
    if product.category == "Mobile":
        detail_product = get_object_or_404(Mobile, product=product)
    else:
        detail_product = get_object_or_404(Laptop, product=product)

    return render(request, "product_detail.html", {'detail_product': detail_product, 'base_template': base_template, 'user': request.user.is_product_admin})


# edit product detail
@login_required()
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
@login_required()
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
@login_required()
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
                login(request, user)
                messages.info(
                    request, f"You are now logged in as @{username}.")
                if user.is_product_admin == 'Customer':
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
                login(request, user)
                messages.info(
                    request, f"You are now logged in as @{username}.")
                if user.is_product_admin == 'Customer':
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
    return redirect("home")


#to display the profile details
@login_required()
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.user.is_product_admin == "Admin":
        base_template = 'admin/admin_base.html'
    else:
        base_template = 'customer/base.html'
    return render(request, "profile.html", context={"profile": profile, "base_template": base_template})


#to edit the profuile detaila
@login_required()
def edit_profile(request):
    if request.user.is_product_admin == "Admin":
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
