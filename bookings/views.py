from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from reviews.models import Review 

from .models import Booking, Payment
from listings.models import Listing
from accounts.models import UserProfile  # if you want to check host status
from .forms import BookingForm  # import our custom form

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
        self.listing = get_object_or_404(Listing, pk=kwargs["listing_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the user in so __init__ can prefill address
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # form_valid now needs both user and listing
        booking = form.form_valid(user=self.request.user, listing=self.listing)
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


class PaymentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Display payment information for a booking. Only the guest or the host may view.
    """
    model = Payment
    template_name = "bookings/payment_detail.html"
    context_object_name = "payment"

    def test_func(self):
        payment = self.get_object()
        booking = payment.booking
        user = self.request.user
        return (booking.guest == user) or (booking.listing.host == user)

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to view that payment.")
        return redirect("bookings:booking_list")


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