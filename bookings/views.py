from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    View,
    FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from reviews.models import Review 

from .models import Booking, Payment
from listings.models import Listing
from accounts.models import UserProfile  # if you want to check host status
from .forms import BookingForm, PaymentDetailForm

from django.urls import reverse
from django.conf import settings
import stripe



class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(guest=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Compute all the listing IDs that this user has already reviewed:
        reviewed_ids = (
            Review.objects
            .filter(guest=self.request.user)
            .values_list("listing_id", flat=True)
        )
        # Pass that QuerySet (or list) to the template:
        context["reviewed_ids"] = set(reviewed_ids)
        return context


class BookingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Show details for a single booking. Only the guest or the host of the listing
    can view this page.
    """
    model = Booking
    template_name = "bookings/booking_detail.html"
    context_object_name = "booking"

    def test_func(self):
        booking = self.get_object()
        user = self.request.user
        # Allow if the user is the booking’s guest OR the host of the listing:
        return (booking.guest == user) or (booking.listing.host == user)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to view that booking.")
        return redirect("bookings:booking_list")


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/booking_form.html"

    def dispatch(self, request, *args, **kwargs):
        # Grab the listing we're booking
        self.listing = get_object_or_404(Listing, pk=kwargs["listing_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Use your form.save(user, listing) helper
        booking = form.save(user=self.request.user, listing=self.listing)
        return redirect(booking.get_absolute_url())


class BookingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/booking_form.html"

    def get_initial(self):
        initial = super().get_initial()
        booking = self.get_object()
        # Format existing dates as "YYYY-MM-DD to YYYY-MM-DD"
        initial["date_range"] = f"{booking.check_in} to {booking.check_out}"
        return initial

    def test_func(self):
        booking = self.get_object()
        return booking.guest == self.request.user and booking.status == "pending"

    def handle_no_permission(self):
        messages.error(self.request, "You cannot edit this booking.")
        return redirect("bookings:booking_list")


class BookingCancelView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    A simple view that, upon POST, sets booking.status = "cancelled"
    and redirects back to booking_list. Only the guest can cancel if status == "pending".
    """
    def get_object(self):
        return get_object_or_404(Booking, pk=self.kwargs["pk"])

    def test_func(self):
        booking = self.get_object()
        return (booking.guest == self.request.user) and (booking.status == "pending")

    def handle_no_permission(self):
        messages.error(self.request, "You cannot cancel this booking.")
        return redirect("bookings:booking_list")

    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = "cancelled"
        booking.save()
        messages.success(request, "Your booking has been cancelled.")
        return redirect("bookings:booking_list")


class PaymentDetailView(LoginRequiredMixin, FormView):
    template_name = "bookings/payment_detail.html"
    form_class = PaymentDetailForm

    def dispatch(self, request, *args, **kwargs):
        # Load booking & its Payment
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
        ctx["booking"] = self.booking
        ctx["stripe_public_key"] = settings.STRIPE_PUBLISHABLE_KEY

        # Create or retrieve a PaymentIntent
        stripe.api_key = settings.STRIPE_SECRET_KEY
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
            intent = stripe.PaymentIntent.retrieve(self.payment.stripe_payment_intent)

        ctx["stripe_client_secret"] = intent.client_secret
        return ctx

    def form_valid(self, form):
        # Save billing address
        for field, val in form.cleaned_data.items():
            setattr(self.payment, field, val)
        self.payment.save()

        # Re-render with session in context for the JS to pick up
        return render(self.request, self.template_name, self.get_context_data(form=form))


def create_checkout_session(request, listing_id):
    # Look up your listing/booking and calculate amount (in pence)
    listing = get_object_or_404(Listing, pk=listing_id)
    YOUR_DOMAIN = request.build_absolute_uri('/')[:-1]  # e.g. https://localhost:8000

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],           # cards only; Apple/Google Pay added automatically
        line_items=[{
            'price_data': {
                'currency': 'gbp',
                'unit_amount': int(listing.price * 100),  # pence
                'product_data': {
                    'name': listing.title,
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=YOUR_DOMAIN + reverse('payments:success') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=YOUR_DOMAIN + reverse('payments:cancel'),
    )
    return redirect(session.url, code=303)

def payment_success(request):
    return render(request, 'payments/success.html')

def payment_cancel(request):
    return render(request, 'payments/cancel.html')


class HostBookingListView(LoginRequiredMixin, ListView):
    """
    Show all bookings for listings where request.user is the host.
    """
    model = Booking
    template_name = "bookings/host_booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        # Get all listings for which the user is the host
        return Booking.objects.filter(listing__host=self.request.user).order_by("-created_at")

class ConfirmBookingView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Only the host of the listing may confirm a pending booking.
    """
    def get_object(self):
        return get_object_or_404(Booking, pk=self.kwargs["pk"])

    def test_func(self):
        booking = self.get_object()
        return booking.listing.host == self.request.user and booking.status == "pending"

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to confirm this booking.")
        return redirect("bookings:host_booking_list")

    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = "confirmed"
        booking.save()
        messages.success(request, "Booking confirmed successfully.")
        return redirect("bookings:host_booking_list")

class StripeCheckoutView(LoginRequiredMixin, View):
    def get(self, request, booking_pk):
        booking = get_object_or_404(Booking, pk=booking_pk, guest=request.user)
        payment = booking.payment

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Booking #{booking.pk} for {booking.listing.title}",
                    },
                    "unit_amount": booking.total_price * 100,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=settings.STRIPE_SUCCESS_URL + f"?booking_id={booking.pk}",
            cancel_url=settings.STRIPE_CANCEL_URL + f"?booking_id={booking.pk}",
            billing_address_collection="required",
            customer_email=request.user.email,
            metadata={
                "booking_id": booking.pk,
                # optionally include the address fields
                "street_address": payment.street_address,
                "city": payment.city,
                "postcode": payment.postcode,
                "country": payment.country,
            },
        )
        # store PaymentIntent if needed
        payment.stripe_payment_intent = session.payment_intent
        payment.save()
        return redirect(session.url, code=303)
