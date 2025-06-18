# payments/views.py

import stripe
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from bookings.models import Booking
from .models import Payment
from .forms import PaymentDetailForm

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentDetailView(LoginRequiredMixin, FormView):
    template_name = "payments/payment_detail.html"
    form_class = PaymentDetailForm

    def dispatch(self, request, *args, **kwargs):
        # load booking and ensure only the guest can access
        self.booking = get_object_or_404(
            Booking, pk=kwargs["booking_pk"]
        )
        if request.user != self.booking.guest:
            messages.error(request, "Please contact the guest to pay for this booking.")
            return redirect("bookings:booking_detail", self.booking.pk)

        # get or create Payment record for this booking
        self.payment, _ = Payment.objects.get_or_create(booking=self.booking)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            "street_address": self.payment.street_address,
            "city": self.payment.city,
            "postcode": self.payment.postcode,
            "country": self.payment.country,
        }

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        ctx["booking"] = self.booking
        ctx["stripe_public_key"] = settings.STRIPE_PUBLISHABLE_KEY

        # Create or retrieve a Stripe PaymentIntent
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
        # save billing address fields
        for f, v in form.cleaned_data.items():
            setattr(self.payment, f, v)
        self.payment.save()

        # stay on payment page so client JS can confirm payment
        return render(self.request, self.template_name, self.get_context_data())


class StripeCheckoutView(LoginRequiredMixin, View):
    """
    Spins up a Stripe Checkout Session and redirects there.
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
                    "product_data": {"name": f"Booking #{booking.pk}: {booking.listing.title}"},
                    "unit_amount": int(booking.total_price * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=settings.STRIPE_SUCCESS_URL + f"?booking_id={booking.pk}",
            cancel_url=settings.STRIPE_CANCEL_URL + f"?booking_id={booking.pk}",
            customer_email=request.user.email,
            billing_address_collection="required",
            metadata={"booking_id": booking.pk},
        )
        payment.stripe_payment_intent = session.payment_intent
        payment.save()

        return redirect(session.url, code=303)


def payment_success(request):
    """
    Handle successful payments:
     - mark booking confirmed
     - send confirmation e-mails to both guest and host
     - render the success page
    """
    booking_id = request.GET.get("booking_id")
    booking = None
    if booking_id:
        booking = get_object_or_404(Booking, pk=booking_id, guest=request.user)

        # mark payment succeeded
        payment = getattr(booking, "payment", None)
        if payment and payment.status != "succeeded":
            payment.status = "succeeded"
            payment.save()

        # confirm the booking
        if booking.status != "confirmed":
            booking.status = "confirmed"
            booking.save()

        # build subject & message
        subject = f"Your WoofAway booking #{booking.pk} is confirmed"
        detail_url = request.build_absolute_uri(
            reverse("bookings:booking_detail", args=[booking.pk])
        )
        message = (
            f"Booking Confirmation\n\n"
            f"Booking #: {booking.pk}\n"
            f"Listing: {booking.listing.title}\n"
            f"Location: {booking.listing.location}\n"
            f"Check-in: {booking.check_in}\n"
            f"Check-out: {booking.check_out}\n"
        )
        if hasattr(booking, "num_dogs"):
            message += f"Number of Dogs: {booking.num_dogs}\n"
        message += (
            f"Total Price: £{booking.total_price}\n\n"
            f"Host: {booking.listing.host.username} ({booking.listing.host.email})\n"
            f"View your booking: {detail_url}\n"
        )

        # send to guest and host
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.guest.email, booking.listing.host.email],
            fail_silently=False,
        )

    return render(request, "payments/success.html", {"booking": booking})


def payment_cancel(request):
    return render(request, "payments/cancel.html")
