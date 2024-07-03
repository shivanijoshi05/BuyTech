from django.db import models

from djangoapps.user_account.models import CustomUser

# Create your models here.

#to store the Product details from user
CATEGORY = (
    ('Mobile', 'Mobile'),
    ('Laptop', 'Laptop')
)
class Product(models.Model):
    """
    A model for storing product details.

    The `Product` model stores details about a product, including its name, price,
    category, description, and image. It also includes methods for retrieving
    products by various criteria, such as admin, ID, or category.
    """

    product_admin = models.ForeignKey(
        CustomUser,  on_delete=models.CASCADE,
        default=None, related_name='product_admin')
    name = models.CharField(max_length=60, unique=True)
    price = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    category = models.CharField(
        'category', choices=CATEGORY, max_length=128,default='Mobile')
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to='uploads/products/')

    def __str__(self):
        return self.name
  
    @property
    def in_stock(self):
        return self.stock > 0
    
    @staticmethod
    def get_products():
        return Product.objects.all()
    @staticmethod
    def get_products_by_admin(product_admin):
        if product_admin:
            return Product.objects.filter(product_admin=product_admin).select_related('product_admin')
        
    @staticmethod
    def get_products_by_id(id):
        if id:
            return Product.objects.filter(id=id) 
    @staticmethod
    def get_products_by_category(category):
        if category:
            return Product.objects.filter(category=category)


# to store the Mobile details from user
class Mobile(models.Model):
    """
    A model for storing mobile details.

    The `Mobile` model  details of a mobile product, including its brand, screen size, 
    operating system, battery capacity, and color. This model has a foreign key relationship
    with the Product model, as each Mobile product is associated with one Product instance.
    """
    BRAND_CHOICES = [
        ('Apple', 'Apple'),
        ('Samsung', 'Samsung'),
        ('OnePlus', 'OnePlus'),
        ('Xiaomi', 'Xiaomi'),
        ('Google', 'Google'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="mobiles")
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    screen_size = models.DecimalField(max_digits=4, decimal_places=2)
    os = models.CharField(max_length=50)
    battery = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name


# to store the Laptop details from user
class Laptop(models.Model):
    """
    A model for storing laptop details.

    The `Laptop` model  details of a laptop product, including its brand, screen size, processor, 
    RAM, storage capacity, and color. This model has a foreign key relationship with the 
    Product model, as each Laptop product is associated with one Product instance.
    """
    BRAND_CHOICES = [
        ('Apple', 'Apple'),
        ('Dell', 'Dell'),
        ('Lenovo', 'Lenovo'),
        ('HP', 'HP'),
        ('Acer', 'Acer'),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="laptops")
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    screen_size = models.DecimalField(max_digits=4, decimal_places=2)
    processor = models.CharField(max_length=50)
    ram = models.PositiveIntegerField()
    storage = models.PositiveIntegerField()
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name
