from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from djangoapps.cart.forms import ShippingAddressForm
from djangoapps.cart.models import Cart, ShippingAddress
from djangoapps.order.models import Order, OrderItem
from djangoapps.product.models import Product

from .decorators import admin_login_required
from .forms import CouponForm
from .models import Contact, Coupon

""" customer site views """
# home page
def home(request):
    return render(request, "customer/home.html")


# order history of user
@login_required
def customer_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "customer/your_orders.html", context={"orders": orders})


# about page
def about(request):
    return render(request, "customer/about.html")


# contact page
def contact(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        msg = request.POST["msg"]
        contact = Contact.objects.create(name=name, email=email, phone=phone, msg=msg)
        if request.user.is_authenticated:
            contact.user = request.user
            contact.save()
    return render(request, "customer/contact.html")


# to apply coupon
@login_required
def apply_coupon(request, code):
    cart = get_object_or_404(Cart, user=request.user) or Cart.objects.create(
        user=request.user
    )
    coupon_form = CouponForm(request.POST)
    if coupon_form.is_valid():
        code = coupon_form.cleaned_data["code"]
    if code:
        try:
            coupon = get_object_or_404(Coupon, code=code)
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
            return JsonResponse({"success": False, "message": "Invalid coupon code."})
        # import pdb; pdb.set_trace()
        if cart.apply_coupon(coupon):
            return JsonResponse(
                {
                    "success": True,
                    "message": "Coupon applied.",
                    "total": cart.get_cart_total(),
                    "coupon_discount": cart.get_discount(),
                    "discount_amount": cart.discount_amount,
                }
            )
        else:
            return JsonResponse({"success": False, "message": "Invalid coupon code."})

    return JsonResponse({"success": False, "message": "Invalid coupon form data."})


# to remove coupon
@login_required
def remove_coupon(request):
    if request.method != "POST":
        return JsonResponse({"messages": "Invalid request method"}, status=400)
    cart_id = request.POST.get("cart_id")
    cart = get_object_or_404(Cart, pk=cart_id)
    if cart.coupon_use:
        cart.coupon_use.used -= 1
        cart.coupon_use = None
    cart.save()
    response_data = {
        "total": cart.get_cart_total(),
        "coupon_discount": cart.get_discount(),
        "discount_amount": cart.discount_amount,
        "message": "Coupon removed successfully.",
    }
    return JsonResponse(response_data)


# cart checkout
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    shipping_address = ShippingAddress.objects.filter(
        cart=cart, user=request.user
    ).first()
    if request.method == "POST":
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.cart = cart
            shipping_address.save()
            form = ShippingAddressForm(instance=shipping_address)
    else:
        form = ShippingAddressForm()
    cart_items = cart.items()
    return render(
        request,
        "customer/checkout.html",
        context={
            "cart": cart,
            "form": form,
            "cart_items": cart_items,
            "shipping_address": shipping_address,
            'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        },
    )



""" product admin site """
# dashboard for admin
@admin_login_required
def product_admin(request):
    product_admin = request.user
    products = Product.get_products_by_admin(product_admin=product_admin)
    return render(request, "admin/product_admin.html", context={"products": products})


# to display the orders
@admin_login_required
def orders(request):
    placed_orders = []
    # Retrieve orders that belong to the admin's products
    orders = Order.objects.all().order_by("-created_at")
    # Iterate through the orders and retrieve order items for admin's products
    for order in orders:
        order_items = OrderItem.objects.filter(
            order=order, product__product_admin=request.user
        )
        if order_items.exists():
            placed_orders.append(order)
            continue
    context = {"orders": placed_orders}
    return render(request, "admin/orders.html", context)
