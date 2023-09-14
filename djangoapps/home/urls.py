from django.urls import path
from . import views

urlpatterns = [
    # customer site pages
    path('', views.home, name='home'),
    path('your-orders/', views.customer_orders, name='your_orders'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # coupon and checkout
    path('coupon/apply/<str:code>/', views.apply_coupon, name='apply_coupon'),
    path('coupon/remove/', views.remove_coupon, name='remove_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    
    # admin site pages
    path('product-admin/', views.product_admin, name='product_admin'),
    path('orders/', views.orders, name='orders'),
]
  
