# messaging/urls.py

from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.InboxView.as_view(), name="inbox"),
    path("conversation/<int:pk>/", views.ConversationDetailView.as_view(), name="conversation_detail"),
    path("conversation/create/<int:listing_id>/", views.CreateConversationView.as_view(), name="conversation_create"),
]
