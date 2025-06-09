from django.urls import path
from . import views
from .views import StripeCheckoutView

app_name = "bookings"

urlpatterns = [
    path("", views.BookingListView.as_view(), name="booking_list"),
    path("create/<int:listing_id>/", views.BookingCreateView.as_view(), name="booking_create"),
    path("<int:pk>/", views.BookingDetailView.as_view(), name="booking_detail"),
    path("<int:pk>/edit/", views.BookingUpdateView.as_view(), name="booking_edit"),
    path("<int:pk>/cancel/", views.BookingCancelView.as_view(), name="booking_cancel"),
    path("payment/<int:booking_pk>/", views.PaymentDetailView.as_view(), name="payment_detail"),
    path("checkout/<int:booking_pk>/", StripeCheckoutView.as_view(), name="stripe_checkout"),
    path("host/", views.HostBookingListView.as_view(), name="host_booking_list"),
    path("<int:pk>/confirm/", views.ConfirmBookingView.as_view(), name="booking_confirm"),
]
