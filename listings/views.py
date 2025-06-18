from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Listing
from .forms import ListingForm


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
    form_class = ListingForm
    template_name = "listings/listing_form.html"
    success_url = reverse_lazy("listings:listing_list")
    action = "create"

    def form_valid(self, form):
        # automatically set the host to the current user
        form.instance.host = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["view"] = self
        return ctx


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    form_class = ListingForm
    template_name = "listings/listing_form.html"
    success_url = reverse_lazy("listings:listing_list")
    action = "edit"

    def test_func(self):
        # only allow the owner to edit
        return self.get_object().host == self.request.user

    def handle_no_permission(self):
        # optional: return 404 rather than redirect to login
        raise Http404("You do not have permission to edit this listing.")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["view"] = self
        ctx["listing"] = self.get_object()
        return ctx


class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    template_name = "listings/listing_confirm_delete.html"
    success_url = reverse_lazy("listings:listing_list")

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            # Already deleted (or never existed) → just go back to list
            return redirect(self.success_url)

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.host or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.contrib import messages
        messages.error(self.request, "You do not have permission to delete that listing.")
        return redirect(self.success_url)
