from django.urls import path
from . import views

urlpatterns = [ 
               
  path('create/', views.create_order, name='create_order'),
  path('<int:order_id>/view/',
         views.detail_order_view, name='detail_order_view'),
  path('update/order-status/',
         views.update_order_status, name='update_order_status'),
  
]
