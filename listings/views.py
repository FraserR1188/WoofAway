from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

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
    action = "create"

    def form_valid(self, form):
        # automatically set the host to the current user
        form.instance.host = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Your listing was created successfully!")
        return response

    def get_success_url(self):
        # redirect to the newly created listing’s detail page
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["view"] = self
        return ctx


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    form_class = ListingForm
    template_name = "listings/listing_form.html"
    action = "edit"

    def test_func(self):
        # only allow the owner to edit
        return self.get_object().host == self.request.user

    def handle_no_permission(self):
        raise Http404("You do not have permission to edit this listing.")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Listing updated successfully.")
        return response

    def get_success_url(self):
        # redirect to the updated listing’s detail page
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["view"] = self
        ctx["listing"] = self.get_object()
        return ctx


class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    template_name = "listings/listing_confirm_delete.html"
    success_url = "/listings/"

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
        messages.error(self.request, "You do not have permission to delete that listing.")
        return redirect(self.success_url)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, "Listing deleted successfully.")
        return response
