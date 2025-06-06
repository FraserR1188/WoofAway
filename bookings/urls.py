from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    # We’ll uncomment these once views exist:
    # path("", views.BookingListView.as_view(), name="booking_list"),
    # path("create/<int:listing_id>/", views.BookingCreateView.as_view(), name="booking_create"),
    # path("<int:pk>/", views.BookingDetailView.as_view(), name="booking_detail"),
    # path("<int:pk>/edit/", views.BookingUpdateView.as_view(), name="booking_edit"),
    # path("<int:pk>/cancel/", views.BookingCancelView.as_view(), name="booking_cancel"),
    # path("payment/<int:pk>/", views.PaymentDetailView.as_view(), name="payment_detail"),
]
