"""WoofAway URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home app
    path("", include(("home.urls", "home"), namespace="home")),

    # Allauth (login, signup, logout, etc.)
    path("accounts/", include("allauth.urls")),

    # Accounts (profile, edit)
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),

    # Listings app
    path("listings/", include(("listings.urls", "listings"), namespace="listings")),

    # Bookings app
    path("bookings/", include(("bookings.urls", "bookings"), namespace="bookings")),

    # Reviews app
    path("reviews/", include(("reviews.urls", "reviews"), namespace="reviews")),

    # Messaging app
    path("messages/", include(("messaging.urls", "messaging"), namespace="messaging")),

    #Payments app
    path("payments/", include("payments.urls", namespace="payments")),

]

handler404 = "home.views.page_not_found"