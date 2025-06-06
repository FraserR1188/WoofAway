from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_host", "profile_image")
    list_filter = ("is_host",)
    search_fields = ("user__username", "user__email")
