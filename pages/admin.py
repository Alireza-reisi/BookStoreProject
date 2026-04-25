from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "subject",
        "short_message",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "subject",
        "message",
    )

    list_filter = ("created_at",)

    readonly_fields = (
        "name",
        "email",
        "subject",
        "message",
        "created_at",
    )

    ordering = ("-created_at",)

    def short_message(self, obj):
        return obj.message[:40] + "..." if len(obj.message) > 40 else obj.message

    short_message.short_description = "خلاصه پیام"
