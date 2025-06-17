from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView
from .models import Listing


class ListingListView(ListView):
    model = Listing
    template_name = "listings/listing_list.html"
    context_object_name = "listings"
    # paginate_by = 12  # optional


class ListingDetailView(DetailView):
    model = Listing
    template_name = "listings/listing_detail.html"
    context_object_name = "listing"


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    template_name = "listings/listing_form.html"
    fields = [
        "category", "title", "description", "location",
        "price_per_night", "is_accessible", "dog_policy", "image"
    ]
    success_url = reverse_lazy("listings:listing_list")

    def form_valid(self, form):
        # automatically set the host to the current user
        form.instance.host = self.request.user
        return super().form_valid(form)


class ListingUpdateView(LoginRequiredMixin,
                        UserPassesTestMixin,
                        UpdateView):
    model = Listing
    template_name = "listings/listing_form.html"
    fields = [
        "category", "title", "description", "location",
        "price_per_night", "is_accessible", "dog_policy", "image"
    ]
    success_url = reverse_lazy("listings:listing_list")

    def test_func(self):
        # only allow the owner to edit
        return self.get_object().host == self.request.user

    def handle_no_permission(self):
        # optional: return 404 rather than redirect to login
        raise Http404("You do not have permission to edit this listing.")


class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    template_name = "listings/listing_confirm_delete.html"
    success_url = reverse_lazy("listings:listing_list")

    def test_func(self):
        # only the owner or a superuser can delete
        listing = self.get_object()
        return self.request.user == listing.host or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(self.request, "You do not have permission to delete that listing.")
        return redirect("listings:listing_list")