from django.contrib import admin
from django.urls import path
from . import views
from .views import AboutPageView

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path("about/", AboutPageView.as_view(), name="about"),
]