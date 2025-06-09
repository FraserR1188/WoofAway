from django.urls import path
from .views import PaymentDetailView, payment_success, payment_cancel

app_name = "payments"

urlpatterns = [
    path(
        "payment/<int:booking_pk>/",
        PaymentDetailView.as_view(),
        name="detail",
    ),
    path("success/", payment_success, name="success"),
    path("cancel/",  payment_cancel,  name="cancel"),
]
