from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Conversation, Message
from listings.models import Listing
from bookings.models import Booking  # import Booking for context


class InboxView(LoginRequiredMixin, ListView):
    """
    Show all conversations for the logged-in user.
    """
    model = Conversation
    template_name = "messaging/inbox.html"
    context_object_name = "conversations"
    paginate_by = 10

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)


class ConversationDetailView(LoginRequiredMixin, DetailView):
    """
    Show all messages in a conversation, plus a form to send a new message.
    """
    model = Conversation
    template_name = "messaging/conversation_detail.html"
    context_object_name = "conversation"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        convo = self.get_object()
        # retrieve the most recent booking between these participants and listing
        booking = Booking.objects.filter(
            listing=convo.listing,
            guest=self.request.user
        ).order_by('-created_at').first()
        ctx['booking'] = booking
        return ctx

    def post(self, request, *args, **kwargs):
        convo = self.get_object()
        if request.user not in convo.participants.all():
            messages.error(request, "You do not have permission to message in this conversation.")
            return redirect("messaging:inbox")
        text = request.POST.get("message_text", "").strip()
        if text:
            Message.objects.create(
                conversation=convo,
                sender=request.user,
                text=text
            )
        return redirect("messaging:conversation_detail", convo.pk)


class CreateConversationView(LoginRequiredMixin, View):
    """
    When a guest clicks “Message Host” on a booking detail,
    this view creates or retrieves the one conversation between guest + host + listing.
    """
    def get(self, request, listing_id, *args, **kwargs):
        listing = get_object_or_404(Listing, pk=listing_id)
        host = listing.host
        guest = request.user

        # Prevent host messaging themselves
        if host == guest:
            messages.error(request, "You cannot message yourself.")
            return redirect("listings:listing_detail", listing_id)

        # Look for existing conversation between these two on this listing:
        convo = Conversation.objects.filter(
            listing=listing,
            participants=host
        ).filter(
            participants=guest
        ).first()

        if not convo:
            convo = Conversation.objects.create(listing=listing)
            convo.participants.add(host, guest)

        return redirect("messaging:conversation_detail", convo.pk)
