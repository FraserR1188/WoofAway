# payments/views.py

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from bookings.models import Booking
from .models import Payment
from .forms import PaymentDetailForm

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentDetailView(LoginRequiredMixin, FormView):
    template_name = "payments/payment_detail.html"
    form_class    = PaymentDetailForm

    def dispatch(self, request, *args, **kwargs):
        self.booking = get_object_or_404(
            Booking, pk=kwargs["booking_pk"], guest=request.user
        )
        self.payment, _ = Payment.objects.get_or_create(booking=self.booking)
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
        ctx["booking"]           = self.booking
        ctx["stripe_public_key"] = settings.STRIPE_PUBLISHABLE_KEY

        # ─── Create or retrieve a PaymentIntent ───────────────────────────────
        amount_pence = int(self.booking.total_price * 100)
        if not self.payment.stripe_payment_intent:
            intent = stripe.PaymentIntent.create(
                amount=amount_pence,
                currency="gbp",
                metadata={"booking_id": self.booking.pk},
            )
            self.payment.stripe_payment_intent = intent.id
            self.payment.save()
        else:
            intent = stripe.PaymentIntent.retrieve(
                self.payment.stripe_payment_intent
            )

        ctx["stripe_client_secret"] = intent.client_secret
        return ctx

    def form_valid(self, form):
        # save billing address
        for f, v in form.cleaned_data.items():
            setattr(self.payment, f, v)
        self.payment.save()

        # stay on page so client JS can run confirmCardPayment()
        return render(self.request, self.template_name, self.get_context_data())


class StripeCheckoutView(LoginRequiredMixin, View):
    """
    Spins up a Stripe Checkout Session and 303-redirects to Stripe’s page.
    """
    def get(self, request, booking_pk):
        booking = get_object_or_404(
            Booking, pk=booking_pk, guest=request.user
        )
        payment, _ = Payment.objects.get_or_create(booking=booking)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"Booking #{booking.pk}: {booking.listing.title}",
                    },
                    "unit_amount": int(booking.total_price * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=settings.STRIPE_SUCCESS_URL + f"?booking_id={booking.pk}",
            cancel_url= settings.STRIPE_CANCEL_URL + f"?booking_id={booking.pk}",
            customer_email=request.user.email,
            billing_address_collection="required",
            metadata={"booking_id": booking.pk},
        )
        payment.stripe_payment_intent = session.payment_intent
        payment.save()

        return redirect(session.url, code=303)


def payment_success(request):
    booking_id = request.GET.get("booking_id")
    booking = None
    if booking_id:
        booking = get_object_or_404(Booking, pk=booking_id, guest=request.user)

        # 1) Mark the Payment record as succeeded
        payment = getattr(booking, "payment", None)
        if payment and payment.status != "succeeded":
            payment.status = "succeeded"
            payment.save()

        # 2) Update the Booking status to confirmed
        if booking.status != "confirmed":
            booking.status = "confirmed"
            booking.save()

    return render(request, "payments/success.html", {"booking": booking})


def payment_cancel(request):
    return render(request, "payments/cancel.html")
