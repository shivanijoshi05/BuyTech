from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.mail import EmailMessage
from django.db import models
from django.db.models.signals import post_save
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db import transaction

#user manager to handle custom fields in USER model
class CustomUserManager(UserManager):
    """
    Custom user manager that adds `user_type` and `is_approved` fields.

    Overrides the `create_user` and `create_superuser` methods to ensure that
    these fields are set correctly.
    """
    def create_user(self, user_type, username, email, password=None, **kwargs):
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(user_type=user_type,
                          username=username, email=email, **kwargs)
        user.set_password(password)

        # set is_approved to True by default for users with user_type "Customer"
        if user.user_type == 'Customer':
            user.is_approved = False

        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(user_type='Admin', email=email,username=username,password=password)
        user.is_superuser = True
        user.is_approved = True
        user.is_staff = True
        user.save()

        return user

    

# to create custom user details from USER class
class CustomUser(AbstractUser):
    """
    Custom user model that adds `user_type` and `is_approved` fields.

    Overrides the `save` method to set `is_approved` and send an email to the user.
    """

    USER_TYPE = (
        ('Admin', 'Admin'),
        ('Customer', 'Customer')
    )
    user_type = models.CharField('user_type',choices=USER_TYPE, max_length=128, default='Customer')
    username = models.CharField('username',max_length=50,unique=True,default="")
    email = models.EmailField('email', unique=True)
    is_approved = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.is_approved = False
            if self.user_type=="Admin":
                # This is a new user, so set is_approved to False and send an email to the user that wants to create admin account
                message = f'Your account with {self.username} has registered and send for product admin approval.'
            else:
                message =f"Welcome to Buytech, you're successfully registered as {self.username}"
            try:
                validate_email(self.email) 
                email = EmailMessage("Successfully Registered", message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.email],
                )
                email.send()
            except ValidationError:
                # Handle the case of an invalid email address
                pass
        super().save(*args, **kwargs)
    

#to store the contact us details from user
class Contact(models.Model):
    """
    Model for storing contact form details.
    """
    user =  models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    msg = models.TextField()
    

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
        default=None)
    name = models.CharField(max_length=60, unique=True)
    price = models.IntegerField(default=0)
    category = models.CharField(
        'category', choices=CATEGORY, max_length=128,default='Mobile')
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to='uploads/products/')

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_products():
        return Product.objects.all()
    @staticmethod
    def get_products_by_admin(product_admin):
        if product_admin:
            return Product.objects.filter(product_admin=product_admin)
        
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
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
        Product, on_delete=models.CASCADE)
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    screen_size = models.DecimalField(max_digits=4, decimal_places=2)
    processor = models.CharField(max_length=50)
    ram = models.PositiveIntegerField()
    storage = models.PositiveIntegerField()
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name


# to store the profile details from user
class Profile(models.Model):
    """
    A model to store additional details of a user such as profile image, mobile number, 
    bio, and address.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_img = models.ImageField(
        default='uploads/profiles/profile.png', upload_to='uploads/profiles')
    mobile = models.IntegerField(default=0)
    bio = models.TextField(max_length=100, blank=True)
    address = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.user.username

#profile creation
def create_profile(sender, instance, created, *args, **kwargs):
    """
    create_profile: A signal receiver function to automatically create a profile for a 
    newly created user.
    """
    if not created:
        return
    Profile.objects.create(user=instance)
post_save.connect(create_profile, sender=CustomUser)


# to create coupon
class Coupon(models.Model):
    """
    A model `Coupon` used to store coupon details such as code, discount, and 
    usage_limit. 
    """

    DISCOUNT_TYPES = (
        ('Percentage', 'Percentage'),
        ('Fixed', 'Fixed Amount'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default=DISCOUNT_TYPES[1])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_limit = models.PositiveIntegerField(blank=True, default=1)

    def __str__(self):
        return self.code
    
    def calculate_discounted_total(self, total):
        if self.discount_type == 'Percentage':
            return (total-((self.discount / 100) * total))
        else:
            return (total-self.discount)
        
    def calculate_coupon_discount(self,total):
        if self.discount_type == 'Percentage':
            return ((self.discount / 100) * total)
        else:
            return (self.discount)
        
    

#to track the coupon usage for each user
class CouponUse(models.Model):
    """
    A model to track the usage of coupons for each user. It has fields to store the 
    user ID, coupon ID, and the number of times the coupon has been used. It also has 
    a unique constraint to ensure that a user can only use a coupon once
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ('user', 'coupon')
        

#to store cart items 
class Cart(models.Model):
    """
    A Cart model to store cart items, and related functions to manage 
    the cart such as applying or removing coupons, calculating the total cost of 
    the cart, and getting the list of cart items.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    coupon_use = models.ForeignKey(
        CouponUse, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def items(self):
        return CartItem.objects.filter(cart=self)

    def apply_coupon(self, coupon):
        if coupon:
            coupon_use, created = CouponUse.objects.get_or_create(user=self.user, coupon=coupon)
            if coupon_use.used < coupon.usage_limit:
                try:
                    with transaction.atomic():
                        coupon_use.save()
                        self.coupon_use = coupon_use
                        self.discount_amount = coupon.calculate_discounted_total(self.total)
                        self.save()
                    return True
                except Exception as e:
                    print("Error saving data:", e)
        return False

    def save_coupon_use(self):
        coupon_use = self.coupon_use
        if coupon_use:
            coupon_use.used += 1
            coupon_use.save()
        self.coupon_use = None
        self.discount_amount = 0
        self.save()

    def get_cart_total(self):
        self.total = sum(item.get_total() for item in self.items())
        if self.coupon_use:
            if self.total > 0:
                self.discount_amount = self.coupon_use.coupon.calculate_discounted_total(self.total)
                
            else:
                self.discount_amount = 0
        else:
            self.discount_amount = self.total
        self.save()
        return self.total
    
    def get_discount(self):
        if self.coupon_use:
            return self.coupon_use.coupon.calculate_coupon_discount(self.total)
        return 0
        


# to store the cart items details
class CartItem(models.Model):
    """
    A model to store the details of a product added to a cart.
    """
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
   

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total(self):
        return self.product.price * self.quantity


# to store user orders
class Order(models.Model):
    """
    A Order model represents a user's order with their purchased items. 
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_use = models.ForeignKey(
        CouponUse, on_delete=models.SET_NULL, null=True, blank=True)
    billing_address = models.CharField(max_length=150, default='')
    shipping_address = models.CharField(max_length=150, default='')
    
    def __str__(self):
        return f"Order {self.id}"
     
    def placeOrder(self):
        self.save()

# to store the order item details 
class OrderItem(models.Model):
    """
    A OrderItem model represents an item purchased in an order.
    """
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def get_total(self):
        return self.price * self.quantity
    
    @staticmethod
    def calculate_order_items_total(order_items):
        total = sum(item.get_total() for item in order_items)
        return total

# to store the shipping address
class ShippingAddress(models.Model):
    """
    A ShippingAddress model represents a shipping address of an order.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    user =  models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    email = models.EmailField('email')
    address_line1 = models.CharField(max_length=60)
    address_line2 = models.CharField(max_length=60)
    pin_code = models.CharField(max_length=6)
    city = models.CharField(max_length=60)
    state = models.CharField(max_length=60)
    country = models.CharField(max_length=60)
    
    def __str__(self):
        return f"Shipping Address of {self.user.username} for order - {self.cart.id}"
    
    
