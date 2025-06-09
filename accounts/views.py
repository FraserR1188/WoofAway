# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm

@login_required
def view_profile(request):
    """
    Show the logged-in user’s profile with all address fields.
    """
    profile = request.user.profile
    return render(request, "accounts/profile.html", {
        "profile": profile
    })

@login_required
def edit_profile(request):
    """
    Allow the user to update their own UserProfile fields, including address.
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

    return render(request, "accounts/profile_edit.html", {
        "form": form
    })
