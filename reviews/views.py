# reviews/views.py

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Review
from listings.models import Listing

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ["rating", "comment"]
    template_name = "reviews/review_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.listing = get_object_or_404(Listing, pk=kwargs["listing_id"])
        # Prevent hosts from reviewing their own listing:
        if self.listing.host == request.user:
            messages.error(request, "Hosts cannot review their own listing.")
            return redirect("listings:listing_detail", self.listing.pk)
        # Prevent guests from leaving multiple reviews if unique_together enforced:
        if Review.objects.filter(listing=self.listing, guest=request.user).exists():
            messages.error(request, "You have already reviewed this listing.")
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
        return reverse_lazy("listings:listing_detail", args=[self.get_object().listing.pk])


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
        return reverse_lazy("listings:listing_detail", args=[self.get_object().listing.pk])
