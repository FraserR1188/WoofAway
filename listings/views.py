# listings/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Listing

# — Existing ListView —
class ListingListView(ListView):
    model = Listing
    template_name = "listings/listing_list.html"
    context_object_name = "listings"
    # (You can add paginate_by, ordering, etc., later)

# — Stub DetailView —
class ListingDetailView(DetailView):
    model = Listing
    template_name = "listings/listing_detail.html"
    context_object_name = "listing"
    # Later you might override get_context_data() or add permissions

# — Stub CreateView (needs form fields) —
class ListingCreateView(CreateView):
    model = Listing
    template_name = "listings/listing_form.html"
    # For now, let’s say you want to allow creating only title and description.
    fields = ["host", "category", "title", "description", "location", "price_per_night", "is_accessible", "dog_policy", "image"]
    # When the form is valid, redirect back to the listing-list page:
    success_url = reverse_lazy("listings:listing_list")

# — Stub UpdateView (analogous to CreateView) —
class ListingUpdateView(UpdateView):
    model = Listing
    template_name = "listings/listing_form.html"
    fields = ["host", "category", "title", "description", "location", "price_per_night", "is_accessible", "dog_policy", "image"]
    success_url = reverse_lazy("listings:listing_list")
