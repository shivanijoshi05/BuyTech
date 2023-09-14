from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from djangoapps.cart.models import Cart, CartItem, ShippingAddress
from djangoapps.home.decorators import admin_login_required
from .models import Order, OrderItem
from djangoapps.product.models import Product


# create the order status if payment is successful
@login_required
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
                cart_item.product.stock -= cart_item.quantity
                order_item, _ = OrderItem.objects.get_or_create(
                    order=order, product=cart_item.product, quantity=cart_item.quantity, price=cart_item.product.price)
            # Delete cart items
            CartItem.objects.filter(cart=cart).delete()
            cart.save_coupon_use()
            response_data = {'success': True, 'message': 'Order Placed successfully.'}
        else:
            response_data = {'success': False, 'message': 'Cart is empty.'}
    else:
        response_data = {'success': False, 'message': 'Invalid request method.'}

    return JsonResponse(response_data)


# detail order view for past orders
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


# update the order status
@admin_login_required
def update_order_status(request):
    if request.method != 'POST' or request.user.user_type != 'Admin':
        return JsonResponse({'message': 'Invalid request'}, status=400)
    order_item_id = request.POST.get('order_item_id')
    status = request.POST.get('status')
    order_item = OrderItem.objects.get(id=order_item_id)
    order_item.status = status
    order_item.save()
    return JsonResponse({'message': 'Status updated successfully'}, status=200)