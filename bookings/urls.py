# bookings/urls.py

from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.BookingListView.as_view(), name="booking_list"),
    path("create/<int:listing_id>/", views.BookingCreateView.as_view(), name="booking_create"),
    path("<int:pk>/", views.BookingDetailView.as_view(), name="booking_detail"),
    path("<int:pk>/edit/", views.BookingUpdateView.as_view(), name="booking_edit"),
    path("<int:pk>/cancel/", views.BookingCancelView.as_view(), name="booking_cancel"),
    path("host/", views.HostBookingListView.as_view(), name="host_booking_list"),
    path("<int:pk>/confirm/", views.ConfirmBookingView.as_view(), name="booking_confirm"),
]
