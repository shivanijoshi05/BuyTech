from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile


# to create basic profile with user account details after signup
@receiver(post_save, sender=CustomUser, dispatch_uid='save_new_user_profile')
def save_profile(sender, instance, created, **kwargs):
    """
    A function is a signal receiver that is triggered when a new CustomUser instance 
    is created. It creates a Profile instance associated with the newly created user 
    and saves it to the database.
    """
    user = instance
    if created:
        profile = Profile(user=user)
        profile.save()
