# accounts/signals.py
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up  # fires after allauth signup
from .models import UserProfile

@receiver(user_signed_up)
def create_user_profile(request, user, **kwargs):
    """
    This runs when allauth’s signup process successfully creates a new User.
    We’ll make an empty UserProfile for them.
    """
    UserProfile.objects.create(user=user)
