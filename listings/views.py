from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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