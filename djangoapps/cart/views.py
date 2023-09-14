from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, CartItem
from djangoapps.home.forms import CouponForm
from djangoapps.home.models import Coupon
from djangoapps.product.models import Product


# cart view
@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.total = cart.get_cart_total()
    cart.save()
    
    items = CartItem.objects.filter(cart=cart)
    coupons = Coupon.objects.all()
    coupon_form = CouponForm()
    coupon_discount = cart.get_discount()
    
    return render(request, "customer/cart.html", {
        "cart_items": items,
        "cart": cart,
        "coupons": coupons,
        "coupon_form": coupon_form,
        "coupon_discount": coupon_discount,
    })


# adding products to cart
@login_required
def add_to_cart(request, product_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, pk=product_id)
    if product.in_stock:
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += 1
            item.save()
        product.stock -= 1
    else:
        messages.error(request, "This product is out of stock.")
        return redirect("home")
    product.save()
    cart.total = cart.get_cart_total()
    messages.success(request, "Added to cart.")
    return redirect("cart")


# update cart-item
@login_required
def update_cart_item_quantity(request, product_id):
    if request.method == "POST":
        cart = get_object_or_404(Cart, user=request.user)
        product = get_object_or_404(Product, pk=product_id)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        new_quantity = int(request.POST.get("quantity"))

        cart_item.quantity += new_quantity
        if request.POST.get("remove") == "true" or cart_item.quantity == 0:
            if cart_item.quantity == 0:
                product.stock -= new_quantity
            else:
                product.stock += cart_item.quantity
            cart_item.delete()
            product.save()
            return JsonResponse(
                {
                    "success": True,
                    "remove": True,
                    "total": cart.get_cart_total(),
                    "coupon_discount": cart.get_discount(),
                    "discount_amount": cart.discount_amount,
                }
            )

        if (new_quantity > 0 and product.in_stock) or (new_quantity <= 0):
            product.stock -= new_quantity
            product.save()
            cart_item.save()
            return JsonResponse(
                {
                    "success": True,
                    "quantity": cart_item.quantity,
                    "total": cart.get_cart_total(),
                    "coupon_discount": cart.get_discount(),
                    "discount_amount": cart.discount_amount,
                    "remove": False,
                }
            )
    return JsonResponse({"success": False, "message": "This product is out of stock."})
