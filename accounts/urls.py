from django.urls import path, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from .views import SignUpView, ProfileView, EditProfileView

app_name = "accounts"

urlpatterns = [
    # login/logout powered by Django auth
    path(
        "login/",
        LoginView.as_view(template_name="accounts/login.html"),
        name="login"
    ),
    path(
        "logout/",
        LogoutView.as_view(next_page=reverse_lazy("home:index")),
        name="logout"
    ),
    # custom signup from allauth
    path(
        "signup/",
        SignUpView.as_view(),
        name="signup"
    ),
    # profile views
    path(
        "profile/",
        ProfileView.as_view(),
        name="view_profile"
    ),
    path(
        "profile/edit/",
        EditProfileView.as_view(),
        name="edit_profile"
    ),
]
