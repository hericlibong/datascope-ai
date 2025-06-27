# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Feedback


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "username", "email", "is_staff", "is_admin")
    ordering = ("username",)
    search_fields = ("username", "email")
    fieldsets = UserAdmin.fieldsets  # conserve les sections par défaut

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "job_title")

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "analysis",
        "relevance",
        "angles",
        "sources",
        "reusability",
        "message",
        "submitted_at",
    )
    list_filter = (
        "relevance",
        "angles",
        "sources",
        "reusability",
        "submitted_at",
    )
    search_fields = ("user__username", "user__email", "message")
    autocomplete_fields = ("user", "analysis")   # pratique si beaucoup d’entrées
    date_hierarchy = "submitted_at"
    ordering = ("-submitted_at",)
    