from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from djangoapps.home.decorators import admin_login_required
from djangoapps.product.forms import LaptopForm, MobileForm, ProductForm
from djangoapps.product.models import Laptop, Mobile, Product
from rest_framework.response import Response
from rest_framework.views import APIView


# to add or edit products display entered by admin
@admin_login_required
def add_or_edit_product(request, product_id=None):
    product = None
    mobile = None
    laptop = None
    category = None
    laptop_form = None
    mobile_form = None
   
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        category = product.category
        if category == "Mobile":
            mobile = get_object_or_404(Mobile, product=product)
        elif category == "Laptop":
            laptop =get_object_or_404(Laptop, product=product)

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES,instance=product)

        if product_form.is_valid():
            if not category:
                category = request.POST.get('category-input') 
            product = product_form.save(commit=False)
            product.product_admin = request.user
            product.category = category
            product.save()
            if category == 'Mobile':
                mobile_form = MobileForm(request.POST,instance=mobile)
                
                if mobile_form.is_valid():
                    mobile = mobile_form.save(commit=False)
                    mobile.product = product
                    mobile.save()
            elif category == 'Laptop':
                laptop_form = LaptopForm(request.POST,instance=laptop)
                
                if laptop_form.is_valid():
                    laptop = laptop_form.save(commit=False)
                    laptop.product = product
                    laptop.save()

            return redirect('product_admin')  # Redirect to a product list view
    else:
        product_form = ProductForm(instance=product)
        mobile_form = MobileForm(instance=mobile)
        laptop_form = LaptopForm(instance=laptop)
        category = product.category if product else None
        
    return render(request, 'admin/add_products.html', {
        'form': product_form,
        'mobile_form': mobile_form,
        'laptop_form': laptop_form,
        'category': category

    })


# detail product view
@login_required
def detail_product_view(request, product_id):
    if request.user.user_type == "Admin":
        base_template = 'admin/admin_base.html'
    else:
        base_template = 'customer/base.html'
    product = Product.objects.filter(pk = product_id).first()
    if product.category == "Mobile":
        detail_product = Mobile.objects.filter(product=product).select_related('product').first()
    else:
        detail_product = Laptop.objects.filter(product=product).select_related('product').first()

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
    return redirect("product_admin")


# search API
class ProductSearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('query', '')
        products = Product.objects.filter(name__icontains=query)
        product_list_html = render_to_string('product_list.html', {'products': products})
        return JsonResponse({'product_list_html': product_list_html})
    
    
# filter options list API
class FilterOptionsAPIView(APIView):
    def get(self, request):
        laptop_brands = Laptop.objects.values_list('brand', flat=True).distinct()
        laptop_colors = Laptop.objects.values_list('color', flat=True).distinct()
        
        mobile_brands = Mobile.objects.values_list('brand', flat=True).distinct()
        mobile_colors = Mobile.objects.values_list('color', flat=True).distinct()

        # Combine the lists and remove duplicates by converting them to sets and back to lists
        brands = list(set(list(laptop_brands) + list(mobile_brands)))
        colors = list(set(list(laptop_colors) + list(mobile_colors)))

        data = {'brands': brands, 'colors': colors }
        return Response(data)


# filter products API
class FilterProductsAPIView(APIView):
    def get(self, request):
        # Retrieve the category, brand, and color from the query parameters
        category = request.query_params.get('category')
        brands = request.query_params.getlist('brand[]')
        colors = request.query_params.getlist('color[]')

        if request.user.is_authenticated:
            queryset = Product.objects.exclude(product_admin=request.user)
        else:
            queryset = Product.objects.all()

        # Handle the case where no filters are selected (return all products)
        if category == "All" and not brands and not colors:
            product_list_html = render_to_string('product_list.html', {'products': queryset})
            return JsonResponse({'product_list_html': product_list_html})
        # Apply filters based on selected category
        if category != "All":
            queryset = queryset.filter(category=category)
        # Apply filters based on selected brands
        if brands:
            brand_filter = Q()
            for brand in brands:
                brand_filter |= Q(mobiles__brand=brand) | Q(laptops__brand=brand)
            queryset = queryset.filter(brand_filter)
        # Apply filters based on selected colors
        if colors:
            color_filter = Q()
            for color in colors:
                color_filter |= Q(mobiles__color=color) | Q(laptops__color=color)
            queryset = queryset.filter(color_filter)

        # Render the filtered products as HTML
        product_list_html = render_to_string('product_list.html', {'products': queryset})
        return JsonResponse({'product_list_html': product_list_html})
