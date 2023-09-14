from django.urls import path
from . import views

urlpatterns = [     
    path('add/', views.add_or_edit_product, name='add_product'),
    path('<int:product_id>/edit/',
         views.add_or_edit_product, name='edit_product'),
    path('<int:product_id>/view/',
         views.detail_product_view, name='detail_product_view'),
    path('<int:product_id>/delete/',
         views.delete_product, name='delete_product'),
    path('api/product-search/', views.ProductSearchAPIView.as_view(), name='product_search_api'),
    path('api/filter-options/', views.FilterOptionsAPIView.as_view(), name='filter_options_api'),
    path('api/filter-products/', views.FilterProductsAPIView.as_view(), name='filter_products'),
]
