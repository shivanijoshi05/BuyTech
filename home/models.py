from django.contrib.auth.models import User
import datetime
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models



#user manager to handle custom fields in USER model
class UserManager(UserManager):
    def create_user(self, is_product_admin, username, email, password=None, **kwargs):
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(is_product_admin=is_product_admin, username=username,email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, is_product_admin, username,email, password, **kwargs):
      user = self.create_user(is_product_admin,username,email,password,**kwargs)
      user.is_staff = True
      user.is_admin = True
      user.save(using=self._db)
      return user
    

# to create custom user details from USER class
class CustomUser(AbstractUser):
    USER_TYPE = (
        ('Admin', 'Admin'),
        ('Customer', 'Customer')
    )
    is_product_admin = models.CharField('is_product_admin',choices=USER_TYPE, max_length=128, default='Customer')
    username = models.CharField('username',max_length=50,unique=True,default="")
    email = models.EmailField('email', unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['is_product_admin','email']
    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


#to store the contact us details from user
class Contact(models.Model):
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
    product_admin = models.ForeignKey(
        CustomUser,  on_delete=models.CASCADE,
        default=None)
    name = models.CharField(max_length=60, unique=True)
    price = models.IntegerField(default=0)
    category = models.CharField(
        'category', choices=CATEGORY, max_length=128,default='Mobile')
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to='uploads/products/')

    @staticmethod
    def get_products():
        return Product.objects.all()
    @staticmethod
    def get_products_by_admin(product_admin):
        if product_admin:
            return Product.objects.filter(product_admin=product_admin)
        else:
            return Product.get_products()
    @staticmethod
    def get_products_by_id(id):
        if id:
            return Product.objects.filter(id=id) 
        else:
            return Product.get_products()
    @staticmethod
    def get_products_by_category(category):
        if category:
            return Product.objects.filter(category=category)
        else:
            return Product.get_products()

# to store the Mobile details from user
class Mobile(Product):
    BRAND_CHOICES = [
        ('Apple', 'Apple'),
        ('Samsung', 'Samsung'),
        ('OnePlus', 'OnePlus'),
        ('Xiaomi', 'Xiaomi'),
        ('Google', 'Google'),
    ]

    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    screen_size = models.DecimalField(max_digits=4, decimal_places=2)
    os = models.CharField(max_length=50)
    battery = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

# to store the Laptop details from user
class Laptop(Product):
    BRAND_CHOICES = [
        ('Apple', 'Apple'),
        ('Dell', 'Dell'),
        ('Lenovo', 'Lenovo'),
        ('HP', 'HP'),
        ('Acer', 'Acer'),
    ]

    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    screen_size = models.DecimalField(max_digits=4, decimal_places=2)
    processor = models.CharField(max_length=50)
    ram = models.PositiveIntegerField()
    storage = models.PositiveIntegerField()
    color=models.CharField(max_length=50)



# to store the profile details from user
class Profile(models.Model):
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
    if not created:
        return
    Profile.objects.create(user=instance)
post_save.connect(create_profile, sender=CustomUser)


# to create coupon
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    


class CouponUse(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ('user', 'coupon')


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    coupon_use = models.ForeignKey(
        CouponUse, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Cart {self.id}"

    def items(self):
        return CartItem.objects.filter(cart=self)

    def apply_coupon(self, coupon):
        if coupon:
                coupon_use,created = CouponUse.objects.get_or_create(user=self.user, coupon=coupon)
                if coupon_use.used < coupon.usage_limit:
                    coupon_use.save()
                    self.coupon_use = coupon_use
                    coupon.save()
                    self.discount_amount = self.total - coupon.discount
                    self.save()
                    return True
        return False

    def remove_coupon(self):
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
                self.discount_amount = self.total - self.coupon_use.coupon.discount
                self.save()
            else:
                self.discount_amount = 0
        return self.total

# to store the cart items details
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
   

    def __str__(self):
        return f"{self.quantity} x {self.product}"

    def get_total(self):
        return self.product.price * self.quantity



# to store user orders
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Order {self.id}"
     
    def placeOrder(self):
        self.save()

# to store the order item details 
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def get_total(self):
        return self.price * self.quantity
  
