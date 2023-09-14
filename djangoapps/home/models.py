from django.db import models
from djangoapps.user_account.models import CustomUser


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
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
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
        



    
    
