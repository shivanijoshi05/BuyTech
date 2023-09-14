from . import views
from django.urls import path

urlpatterns = [  
    # cart
    path('', views.cart, name='cart'),
    path('<int:product_id>/add/',
         views.add_to_cart, name='add_to_cart'),
    path('<int:product_id>/update/',
         views.update_cart_item_quantity, name='update_cart_item_quantity'),
]
