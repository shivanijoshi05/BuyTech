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
    if request.user.is_authenticated:
        if request.user.user_type == "Admin":
            products = Product.objects.exclude(product_admin=request.user)
        else:
            products = Product.get_products()
    else:
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
    coupon_discount = cart.get_discount()
    return render(request, 'customer/cart.html', {'cart_items': items, 'cart': cart, 'coupons':coupons, 'coupon_form': coupon_form, 'coupon_discount':coupon_discount})


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

@login_required
def update_cart_item_quantity(request, product_id):
    if request.method == "POST":
        cart = get_object_or_404(Cart, user=request.user)
        product = get_object_or_404(Product, pk=product_id)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        new_quantity = int(request.POST.get('quantity'))
        cart_item.quantity += new_quantity
        if request.POST.get('remove') == 'true' or cart_item.quantity <= 0:
            cart_item.delete()
            return JsonResponse({'success': True, 'remove': True})
        
        cart_item.save()

        return JsonResponse({'success': True, 'quantity': cart_item.quantity, 'remove': False})

    return JsonResponse({'success': False, 'message': 'Failed!!'})

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
    # import pdb; pdb.set_trace()
    if cart.apply_coupon(coupon):
        messages.success(request, 'Coupon applied.')
    else:
        messages.error(request, 'Coupon usage limit reached.')
  else:
      messages.error(request, 'Invalid coupon code.')
  return redirect('cart')

def remove_coupon(request):
    if request.method == 'POST':
        cart_id = request.POST.get('cart_id')
        cart =  get_object_or_404(Cart,pk=cart_id)
        cart.coupon_use.used -= 1
        cart.coupon_use = None
        cart.save()
        response_data = {
        'coupon_discount': cart.get_discount(),
        'discount_amount': cart.get_cart_total(),
        'message': 'Coupon removed successfully.'
        }
        return JsonResponse(response_data)

    return JsonResponse({'messages': 'Invalid request method'}, status=400)


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

# create the order status if payment is successful
def create_order(request):
    if request.method == 'POST':
        cart_id = request.POST.get('cart_id')
        billing_address = request.POST.get('billing_address')
        cart = get_object_or_404(Cart, pk=cart_id)
        if cart and cart.items():
            # Create order and order items if the order is placed successfully
            shipping_address = get_object_or_404(ShippingAddress,user=request.user, cart=cart)
            concatenated_address = f'{shipping_address.address_line1}, {shipping_address.address_line2}, {shipping_address.city}, {shipping_address.state}, {shipping_address.pin_code}'
            if not billing_address:
                billing_address=concatenated_address
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
def detail_order_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.user.user_type == "Admin":
        base_template = 'admin/admin_base.html'
        admin_products = Product.objects.filter(product_admin=request.user)
        order_items = OrderItem.objects.filter(order=order,product__in=admin_products)
        if not order_items.exists():
            order_items = OrderItem.objects.filter(order=order)
    else:
        base_template = 'customer/base.html'
        order_items = OrderItem.objects.filter(order=order)
    order_total = OrderItem.calculate_order_items_total(order_items)
    return render(request, 'order_detail.html', {'base_template':base_template,'order': order, 'order_items': order_items, 'order_total':order_total})


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
        contact = Contact.objects.create(name=name, email=email, phone=phone, msg=msg)
        if request.user.is_authenticated:
            contact.user=request.user
            contact.save()
      
    return render(request, 'customer/contact.html')



#product admin site 

#dashboard for admin
@admin_login_required
def product_admin(request):
    return render(request, 'admin/product_admin.html')


# to add or edit products display entered by admin
@admin_login_required
def add_or_edit_product(request, product_id=None):
    product = None
    mobile = None
    laptop = None
    
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        if product.category == "Mobile":
            mobile = get_object_or_404(Mobile, product=product)
        elif product.laptop:
            laptop =get_object_or_404(Laptop, product=product)
  
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        
        if product_form.is_valid():
            category = request.POST.get('category-input')
            product = product_form.save(commit=False)
            product.product_admin = request.user
            product.category = category
            product.save()
            if category == 'Mobile':
                mobile_form = MobileForm(request.POST)
                if mobile_form.is_valid():
                    mobile = mobile_form.save(commit=False)
                    mobile.product = product
                    mobile.save()
            elif category == 'Laptop':
                laptop_form = LaptopForm(request.POST)
                if laptop_form.is_valid():
                    laptop = laptop_form.save(commit=False)
                    laptop.product = product
                    laptop.save()

            return redirect('view_products')  # Redirect to a product list view
    else:
        product_form = ProductForm(instance=product)
        mobile_form = MobileForm(instance=mobile)
        laptop_form = LaptopForm(instance=laptop)

    return render(request, 'admin/add_products.html', {
        'form': product_form,
        'mobile_form': mobile_form,
        'laptop_form': laptop_form
        
    })

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
    placed_orders = []
    # Retrieve orders that belong to the admin's products
    orders = Order.objects.all().order_by('-created_at')
    # Iterate through the orders and retrieve order items for admin's products
    for order in orders:
        order_items = OrderItem.objects.filter(order=order, product__product_admin=request.user)
        if order_items.exists():
            placed_orders.append(order)
            continue
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
