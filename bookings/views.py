from django.shortcuts import get_object_or_404, redirect
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

from .models import Booking, Payment
from listings.models import Listing
from accounts.models import UserProfile  # if you want to check host status


class BookingListView(LoginRequiredMixin, ListView):
    """
    Show all bookings where the current user is the guest.
    """
    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(guest=self.request.user).order_by("-created_at")


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
    """
    Create a new booking for a particular listing ID. We set guest = request.user
    and listing = the listing we fetched, then let the model’s save() auto-calc price.
    """
    model = Booking
    template_name = "bookings/booking_form.html"
    fields = ["check_in", "check_out"]
    # We rely on get_absolute_url() on Booking to redirect after success

    def dispatch(self, request, *args, **kwargs):
        # Retrieve the listing first, or 404 if it does not exist
        self.listing = get_object_or_404(Listing, pk=kwargs["listing_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Before saving, set the guest and listing
        form.instance.guest = self.request.user
        form.instance.listing = self.listing
        # The model’s save() will auto-calc total_price
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listing"] = self.listing
        return context


class BookingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Update an existing booking’s check_in/check_out. Only allowed if the booking is
    still 'pending' and the current user is the guest.
    """
    model = Booking
    template_name = "bookings/booking_form.html"
    fields = ["check_in", "check_out"]

    def test_func(self):
        booking = self.get_object()
        return (booking.guest == self.request.user) and (booking.status == "pending")

    def handle_no_permission(self):
        messages.error(self.request, "You cannot edit this booking.")
        return redirect("bookings:booking_list")

    def form_valid(self, form):
        # After changing dates, total_price will be recalculated by model.save()
        return super().form_valid(form)


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