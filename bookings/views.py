# bookings/views.py

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from reviews.models import Review
from .models import Booking
from listings.models import Listing
from .forms import BookingForm


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(guest=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        reviewed_ids = Review.objects.filter(
            guest=self.request.user
        ).values_list("listing_id", flat=True)
        ctx["reviewed_ids"] = set(reviewed_ids)
        return ctx


class BookingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Booking
    template_name = "bookings/booking_detail.html"
    context_object_name = "booking"

    def test_func(self):
        booking = self.get_object()
        user = self.request.user
        return booking.guest == user or booking.listing.host == user

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to view that booking.")
        return redirect("bookings:booking_list")


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/booking_form.html"

    def dispatch(self, request, *args, **kwargs):
        # grab the listing so we can pass it to the form
        self.listing = get_object_or_404(Listing, pk=kwargs["listing_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        # tell the form which listing to build the num_dogs choices for
        kw["listing"] = self.listing
        return kw

    def form_valid(self, form):
        # form.save(...) now handles guest, listing, num_dogs, total_price
        booking = form.save(user=self.request.user, listing=self.listing)
        return redirect(booking.get_absolute_url())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['listing'] = self.listing
        return ctx


class BookingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = "bookings/booking_form.html"

    def test_func(self):
        booking = self.get_object()
        # only allow editing while still pending
        return booking.guest == self.request.user and booking.status == "pending"

    def handle_no_permission(self):
        messages.error(self.request, "You cannot edit this booking.")
        return redirect("bookings:booking_list")

    def get_initial(self):
        initial = super().get_initial()
        booking = self.get_object()
        initial["date_range"] = f"{booking.check_in} to {booking.check_out}"
        initial["num_dogs"] = booking.num_dogs
        return initial

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        booking = self.get_object()
        # pass the listing so the dropdown is correct
        kw["listing"] = booking.listing
        return kw

    def form_valid(self, form):
        booking = self.get_object()
        # re-save via form.save to recalc price & num_dogs
        updated = form.save(user=self.request.user, listing=booking.listing)
        return redirect(updated.get_absolute_url())


class BookingCancelView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get_object(self):
        return get_object_or_404(Booking, pk=self.kwargs["pk"])

    def test_func(self):
        booking = self.get_object()
        return booking.guest == self.request.user and booking.status == "pending"

    def handle_no_permission(self):
        messages.error(self.request, "You cannot cancel this booking.")
        return redirect("bookings:booking_list")

    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = "cancelled"
        booking.save()
        messages.success(request, "Your booking has been cancelled.")
        return redirect("bookings:booking_list")


class HostBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/host_booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(listing__host=self.request.user).order_by("-created_at")


class ConfirmBookingView(LoginRequiredMixin, UserPassesTestMixin, View):
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
