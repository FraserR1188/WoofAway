# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm

from allauth.account.views import SignupView as _SignupView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy

from .models import UserProfile
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


class SignUpView(_SignupView):
    # optionally override template_name or form_class here
    template_name = "accounts/signup.html"
    # form_class = YourCustomSignupForm  # only if you built one


class ProfileView(LoginRequiredMixin, TemplateView):
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
