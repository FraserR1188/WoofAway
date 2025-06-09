# payments/urls.py
from django.urls import path
from .views import PaymentDetailView, StripeCheckoutView, payment_success, payment_cancel

app_name = "payments"

urlpatterns = [
    path(
        "payment/<int:booking_pk>/",
        PaymentDetailView.as_view(),
        name="detail",
    ),
    path(
        "checkout/<int:booking_pk>/",
        StripeCheckoutView.as_view(),
        name="checkout",
    ),
    path("success/", payment_success, name="success"),
    path("cancel/" , payment_cancel , name="cancel"),
]
