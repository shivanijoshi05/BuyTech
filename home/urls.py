from django.urls import path
from home import views

urlpatterns = [
    # customer site pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # cart
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/',
         views.add_to_cart, name='add_to_cart'),
    path('remove_cart_item/<int:product_id>/',
         views.remove_cart_item, name='remove_cart_item'),
    path('increase_cart_item_quantity/<int:product_id>/',
         views.increase_cart_item_quantity, name='increase_cart_item_quantity'),
    path('decrease_cart_item_quantity/<int:product_id>/',
         views.decrease_cart_item_quantity, name='decrease_cart_item_quantity'),
    path('apply_coupon/<str:code>/', views.apply_coupon, name='apply_coupon'),
    path('remove_coupon', views.remove_coupon, name='remove_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    

    # order
    path('create_order/', views.create_order, name='create_order'),
    path('your_orders/', views.customer_orders, name='your_orders'),
        path('view_orders/<int:order_id>/',
         views.detail_order_view, name='detail_order_view'),

    # product detail view
    path('view_products/<int:product_id>/',
         views.detail_product_view, name='detail_product_view'),

    # admin site pages
    path('product_admin/', views.product_admin, name='product_admin'),
    path('view_products/', views.view_products, name='view_products'),
    path('add_products/', views.add_products, name='add_products'),
    path('edit_product/<int:product_id>/',
         views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/',
         views.delete_product, name='delete_product'),
    path('orders/', views.orders, name='orders'),

    # login/signup/logout
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit_profile/', views.edit_profile, name='edit_profile'),
]
