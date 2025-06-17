# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, UpdateView, DetailView
from django.urls import reverse_lazy

from .models import UserProfile
from .forms import ProfileForm
from allauth.account.views import SignupView as _SignupView


@login_required
def view_profile(request):
    """
    Show the logged-in user’s profile with all address fields.
    """
    profile = request.user.profile
    return render(request, "accounts/profile.html", {"profile": profile})


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

    return render(request, "accounts/profile_edit.html", {"form": form})


class SignUpView(_SignupView):
    template_name = "accounts/signup.html"


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View for the currently logged-in user's profile.
    """
    template_name = "accounts/profile.html"

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx['profile'] = self.request.user.profile
        return ctx


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:view_profile")

    def get_object(self):
        # only let users edit their own profile
        return self.request.user.profile


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    View any user's public profile (read-only).
    """
    model = UserProfile
    template_name = "accounts/profile.html"
    context_object_name = "profile"

    def get_object(self):
        # lookup by profile PK from URL
        return get_object_or_404(UserProfile, pk=self.kwargs.get('pk'))
