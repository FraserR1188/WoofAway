# reviews/views.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from .models import Review
from listings.models import Listing
from bookings.models import Booking


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ["rating", "comment"]
    template_name = "reviews/review_form.html"

    def dispatch(self, request, *args, **kwargs):
        """
        1. Ensure the listing exists (using listing_pk from URL).
        2. Only allow guests who have a confirmed booking on this listing.
        3. Prevent hosts from reviewing their own listing.
        4. Prevent multiple reviews (unique_together).
        """
        listing_pk = kwargs.get("listing_pk")
        self.listing = get_object_or_404(Listing, pk=listing_pk)

        # 1. If the user is the listing’s host, block.
        if self.listing.host == request.user:
            messages.error(request, "Hosts cannot review their own listing.")
            return redirect("listings:listing_detail", self.listing.pk)

        # 2. Check for at least one confirmed booking by this user on this listing.
        has_confirmed = Booking.objects.filter(
            listing=self.listing,
            guest=request.user,
            status="confirmed"
        ).exists()
        if not has_confirmed:
            messages.error(
                request,
                "You must have a confirmed booking on this listing before you can review it."
            )
            return redirect("listings:listing_detail", self.listing.pk)

        # 3. Prevent duplicates:
        already_reviewed = Review.objects.filter(
            listing=self.listing,
            guest=request.user
        ).exists()
        if already_reviewed:
            messages.info(request, "You have already reviewed this listing.")
            return redirect("listings:listing_detail", self.listing.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.guest = self.request.user
        form.instance.listing = self.listing
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("listings:listing_detail", args=[self.listing.pk])


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    fields = ["rating", "comment"]
    template_name = "reviews/review_form.html"

    def test_func(self):
        review = self.get_object()
        return review.guest == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "You cannot edit someone else’s review.")
        return redirect("listings:listing_detail", self.get_object().listing.pk)

    def get_success_url(self):
        return reverse_lazy(
            "listings:listing_detail",
            args=[self.get_object().listing.pk]
        )


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = "reviews/review_confirm_delete.html"

    def test_func(self):
        review = self.get_object()
        return review.guest == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "You cannot delete someone else’s review.")
        return redirect("listings:listing_detail", self.get_object().listing.pk)

    def get_success_url(self):
        return reverse_lazy(
            "listings:listing_detail",
            args=[self.get_object().listing.pk]
        )


class MyReviewsView(LoginRequiredMixin, ListView):
    """
    Show all reviews written by the current user (guest).
    """
    model = Review
    template_name = "reviews/my_reviews.html"
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self):
        return Review.objects.filter(self.request.user).select_related("listing")


class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = "reviews/review_list.html"
    context_object_name = "reviews"
    paginate_by = 10
