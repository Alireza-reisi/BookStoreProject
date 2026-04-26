from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Publisher, Book, Comment, Author


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "english_name", "photo_tag", "slug")
    search_fields = ("name", "english_name")
    prepopulated_fields = {"slug": ("english_name",)}
    ordering = ("name",)

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("name", "english_name", "slug")
        }),
        ("جزئیات", {
            "fields": ("photo", "website", "biography")
        }),
    )

    def photo_tag(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" style="border-radius:4px;" />',
                obj.photo.url
            )
        return "—"

    photo_tag.short_description = "عکس"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "english_name", "image_tag", "slug")
    search_fields = ("name", "english_name", "slug")
    prepopulated_fields = {"slug": ("english_name",)}
    list_filter = ("name",)
    ordering = ("name",)

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("name", "english_name", "slug")
        }),
        ("جزئیات", {
            "fields": ("image", "description"),
            "classes": ("collapse",)
        }),
    )

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" style="border-radius:4px;" />',
                obj.image.url
            )
        return "—"

    image_tag.short_description = "تصویر"


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "english_name", "logo_tag", "website", "slug")
    search_fields = ("name", "english_name", "website", "slug")
    prepopulated_fields = {"slug": ("english_name",)}
    ordering = ("name",)

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("name", "english_name", "slug")
        }),
        ("جزئیات", {
            "fields": ("logo", "website", "description"),
        }),
    )

    def logo_tag(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="50" style="border-radius:4px;" />',
                obj.logo.url
            )
        return "—"

    logo_tag.short_description = "لوگو"


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "publisher",
        "product_type",
        "price",
        "discount_price",
        "final_price_display",
        "stock",
        "is_in_stock_display",
        "status",
        "is_active",
        "cover_tag",
        "created_at",
    )

    list_filter = (
        "product_type",
        "status",
        "is_active",
        "publisher",
        "categories",
        "created_at",
    )

    search_fields = (
        "title",
        "english_title",
        "author__name",
        "publisher__name",
        "publisher__english_name",
        "sku",
        "slug",
    )

    prepopulated_fields = {"slug": ("english_title",)}

    filter_horizontal = ("categories",)

    readonly_fields = (
        "sell_count",
        "view_count",
        "download_count",
        "created_at",
        "updated_at",
        "cover_tag",
    )

    ordering = ("-created_at",)

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "title",
                "english_title",
                "slug",
                "author",
                "publisher",
                "categories",
                "creator",
            )
        }),

        ("اطلاعات تجاری", {
            "fields": (
                "sku",
                "product_type",
                "price",
                "discount_price",
                "stock",
                "status",
                "is_active",
            )
        }),

        ("فایل و تصویر", {
            "fields": (
                "image",
                "cover_tag",
                "file",
            )
        }),

        ("تاریخ‌ها", {
            "fields": (
                "published_date",
                "created_at",
                "updated_at",
            )
        }),

        ("توضیحات", {
            "fields": ("description",),
            "classes": ("collapse",)
        }),

        ("آمار", {
            "fields": (
                "sell_count",
                "view_count",
                "download_count",
            ),
        }),
    )

    # -------------------------
    # Custom Display Methods
    # -------------------------

    @admin.display(description="قیمت نهایی")
    def final_price_display(self, obj):
        return obj.final_price

    @admin.display(boolean=True, description="موجود")
    def is_in_stock_display(self, obj):
        return obj.stock > 0

    def cover_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" style="border-radius:4px;" />',
                obj.image.url
            )
        return "—"

    cover_tag.short_description = "کاور"

    def save_model(self, request, obj, form, change):
        if not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("book", "author", "short_text", "is_active", "created_at")
    list_filter = ("is_active", "created_at", "book")
    search_fields = ("book__title", "author__username", "text")
    ordering = ("-created_at",)

    readonly_fields = ("created_at",)

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("book", "author", "text")
        }),
        ("وضعیت", {
            "fields": ("is_active", "created_at"),
        }),
    )

    def short_text(self, obj):
        return (obj.text[:40] + "…") if len(obj.text) > 40 else obj.text

    short_text.short_description = "خلاصه نظر"
