# payments/views.py
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from bookings.models import Booking
from .models import Payment
from .forms import PaymentDetailForm

class PaymentDetailView(LoginRequiredMixin, FormView):
    template_name = "payments/payment_detail.html"
    form_class = PaymentDetailForm

    def dispatch(self, request, *args, **kwargs):
        self.booking, _ = get_object_or_404(Booking, pk=kwargs["booking_pk"]), None
        self.payment, _ = Payment.objects.get_or_create(booking=self.booking)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            "street_address": self.payment.street_address,
            "city":           self.payment.city,
            "postcode":       self.payment.postcode,
            "country":        self.payment.country,
        }

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["booking"] = self.booking
        ctx["stripe_public_key"] = settings.STRIPE_PUBLISHABLE_KEY
        # create/retrieve PaymentIntent here and add client_secret:
        # ...
        return ctx

    def form_valid(self, form):
        # save address + create PaymentIntent + render with stripe_session_id
        # …
        return render(self.request, self.template_name, ctx)


def payment_success(request):
    """
    Shown after a successful Stripe payment.
    """
    return render(request, "payments/success.html")


def payment_cancel(request):
    """
    Shown if the user cancels or the payment fails.
    """
    return render(request, "payments/cancel.html")

