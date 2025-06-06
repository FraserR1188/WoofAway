# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import ProfileForm

@login_required
def view_profile(request):
    """
    Show the logged-in user’s profile. (We assume a UserProfile always exists
    because the allauth signal created one at signup time.)
    """
    profile = request.user.profile  # because of related_name="profile"
    return render(request, "accounts/profile.html", {"profile": profile})

@login_required
def edit_profile(request):
    """
    Allow the user to update their own UserProfile fields.
    """
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:view_profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile_edit.html", {"form": form})
