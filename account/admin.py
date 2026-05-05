from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import User


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ['phone', 'is_active', 'is_admin', 'is_superuser']
    list_filter = ['is_active', 'is_admin', 'is_superuser']

    fieldsets = [
        (None, {"fields": ["phone", "password", ]}),
        ("permissions", {"fields": ["is_admin", 'is_superuser']}),
    ]

    add_fieldsets = [
        (None, {
            "classes": ["wide"],
            "fields": ["phone", "password1", "password2", "is_admin", 'is_superuser']
        })
    ]

    search_fields = ['phone']
    ordering = ["phone"]
    filter_horizontal = []


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
