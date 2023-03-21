from home.models import CustomUser, Profile
from django.db.models.signals import post_save
from django.dispatch import receiver

#to create basic profile with user account details after signup
@receiver(post_save, sender=CustomUser, dispatch_uid='save_new_user_profile')
def save_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        profile = Profile(user=user)
        profile.save()
