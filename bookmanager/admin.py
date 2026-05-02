from django.contrib import admin
from django.utils.html import format_html
from .forms import CommentAdminForm
from .models import Category, Publisher, Book, Comment, Author, CommentReaction


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "english_name", "photo_tag", "slug", "writing_field", "profession", "nationality")
    search_fields = ("name", "english_name")
    prepopulated_fields = {"slug": ("english_name",)}
    ordering = ("name",)

    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": ("name", "english_name", "slug")
        }),
        ("جزئیات", {
            "fields": ("photo", "biography")
        }),
        ("زمینه کاری", {
            "fields": ("writing_field", "profession", "nationality")
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
        "format",
        "status",
        "is_active",
        "publisher",
        "categories",
        "language",
        "created_at",
    )

    search_fields = (
        "title",
        "english_title",
        "author__name",
        "publisher__name",
        "publisher__english_name",
        "sku",
        "isbn",
        "slug",
    )

    list_select_related = ("author", "publisher")
    filter_horizontal = ("categories",)

    ordering = ("-created_at",)
    list_per_page = 20

    # -------------------------
    # Auto Slug
    # -------------------------
    prepopulated_fields = {"slug": ("english_title",)}

    # -------------------------
    # Readonly Fields
    # -------------------------
    readonly_fields = (
        "sell_count",
        "view_count",
        "download_count",
        "average_rating",
        "created_at",
        "updated_at",
        "cover_tag",
    )

    # -------------------------
    # Fieldsets
    # -------------------------
    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "title",
                "english_title",
                "slug",
                "author",
                "translator",
                "publisher",
                "categories",
                "creator",
            )
        }),

        ("اطلاعات تجاری", {
            "fields": (
                "sku",
                "product_type",
                "format",
                "price",
                "discount_price",
                "stock",
                "status",
                "is_active",
            )
        }),

        ("اطلاعات کتاب", {
            "fields": (
                "isbn",
                "page_count",
                "language",
                "published_date",
            )
        }),

        ("فایل و تصویر", {
            "fields": (
                "image",
                "cover_tag",
                "file",
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
                "average_rating",
            ),
            "classes": ("collapse",)
        }),

        ("تاریخ‌ها", {
            "fields": (
                "created_at",
                "updated_at",
            ),
        }),
    )

    @admin.display(description="قیمت نهایی")
    def final_price_display(self, obj):
        return obj.final_price

    @admin.display(boolean=True, description="موجود")
    def is_in_stock_display(self, obj):
        return obj.is_in_stock()

    @admin.display(description="کاور")
    def cover_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" style="border-radius:6px;" />',
                obj.image.url
            )
        return "—"


    def save_model(self, request, obj, form, change):
        if not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


class CommentReactionInline(admin.TabularInline):
    model = CommentReaction
    extra = 0
    readonly_fields = ("user", "reaction", "created_at")
    can_delete = False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    form = CommentAdminForm

    list_display = (
        "content_object",
        "content_type",
        "user",
        "short_text",
        "likes",
        "dislikes",
        "is_active",
        "created_at",
    )

    readonly_fields = ("created_at", "content_object", "likes", "dislikes")

    fieldsets = (
        ("ارتباط", {
            "fields": (
                "content_type",
                "object_id",
            )
        }),

        ("اطلاعات نظر", {
            "fields": (
                "user",
                "text",
            )
        }),

        ("آمار واکنش", {
            "fields": (
                "likes",
                "dislikes",
            )
        }),

        ("وضعیت", {
            "fields": (
                "is_active",
                "created_at",
                "content_object",
            )
        }),
    )

    def short_text(self, obj):
        return (obj.text[:50] + "…") if len(obj.text) > 50 else obj.text

    short_text.short_description = "خلاصه نظر"

    def likes(self, obj):
        return obj.reactions.filter(reaction="like").count()

    likes.short_description = "تعداد لایک"

    def dislikes(self, obj):
        return obj.reactions.filter(reaction="dislike").count()

    dislikes.short_description = "تعداد دیسلایک"
