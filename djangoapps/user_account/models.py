from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db import models
from django.db.models.signals import post_save


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


# to store the profile details from user
class Profile(models.Model):
    """
    A model to store additional details of a user such as profile image, mobile number, 
    bio, and address.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
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

