# reviews/urls.py

from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("create/<int:listing_id>/", views.ReviewCreateView.as_view(), name="review_create"),
    path("<int:pk>/edit/", views.ReviewUpdateView.as_view(), name="review_edit"),
    path("<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review_delete"),
    path("my/", views.MyReviewsView.as_view(), name="my_reviews"),
]
