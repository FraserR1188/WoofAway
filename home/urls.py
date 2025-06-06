from django.contrib import admin
from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path("my/", views.MyReviewsView.as_view(), name="my_reviews"),
]