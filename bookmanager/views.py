from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Book, Author, Publisher, Category, Comment, CommentReaction
from django.db.models import Prefetch
from .forms import AuthorForm, CommentForm
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.urls import reverse
from django.contrib import messages
import logging
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Count
from django.db.models import Q

logger = logging.getLogger(__name__)


def ReactToCommentView(request, comment_id, reaction_type):
    if not request.user.is_authenticated:
        messages.error(request, "برای لایک یا دیسلایک باید وارد شوید.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    comment = get_object_or_404(Comment, id=comment_id)

    obj, created = CommentReaction.objects.get_or_create(
        user=request.user,
        comment=comment,
        defaults={'reaction': reaction_type}
    )

    if not created:
        obj.reaction = reaction_type
        obj.save()

    return redirect(request.META.get("HTTP_REFERER", "/"))


class BookListView(ListView):
    model = Book
    template_name = "bookmanager/book_list.html"
    context_object_name = "books"
    paginate_by = 12

    def get_queryset(self):
        qs = Book.objects.all()

        # سرچ هدر
        query = self.request.GET.get("Search")
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(author__name__icontains=query) |
                Q(publisher__name__icontains=query)
            ).distinct()

        # پایه annotation برای همه
        qs = qs.annotate(comments_count=Count("comments"))

        categories = self.request.GET.getlist("categories")
        publishers = self.request.GET.getlist("publishers")
        authors = self.request.GET.getlist("authors")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        sort = self.request.GET.get("sort")

        def to_int_list(values):
            result = []
            for val in values:
                try:
                    result.append(int(val))
                except:
                    pass
            return result

        categories = to_int_list(categories)
        publishers = to_int_list(publishers)
        authors = to_int_list(authors)

        # ✅ مرتب‌سازی
        if sort == "name":
            qs = qs.order_by("title")
        elif sort == "newest":
            qs = qs.order_by("-created_at")
        elif sort == "oldest":
            qs = qs.order_by("created_at")
        elif sort == "price_asc":
            qs = qs.order_by("price")
        elif sort == "price_desc":
            qs = qs.order_by("-price")
        elif sort == "popular":
            qs = qs.order_by("-comments_count")

        # ✅ فیلترها
        if categories:
            qs = qs.filter(categories__id__in=categories)
        if publishers:
            qs = qs.filter(publisher__id__in=publishers)
        if authors:
            qs = qs.filter(authors__id__in=authors)
        if min_price and min_price.isdigit():
            qs = qs.filter(price__gte=int(min_price))
        if max_price and max_price.isdigit():
            qs = qs.filter(price__lte=int(max_price))

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # انتخاب‌شده‌ها (برای چک‌باکس‌ها)
        getlist = self.request.GET.getlist
        to_int = lambda x: int(x) if x.isdigit() else None

        context["selected_categories"] = [to_int(c) for c in getlist("categories") if c.isdigit()]
        context["selected_publishers"] = [to_int(p) for p in getlist("publishers") if p.isdigit()]
        context["selected_authors"] = [to_int(a) for a in getlist("authors") if a.isdigit()]

        context["min_price"] = self.request.GET.get("min_price")
        context["max_price"] = self.request.GET.get("max_price")

        context["selected_sort"] = self.request.GET.get("sort", "")

        # داده‌های فیلتر
        context["categories"] = Category.objects.all()
        context["publishers"] = Publisher.objects.all()
        context["authors"] = Author.objects.all()

        return context

    def render_to_response(self, context, **response_kwargs):

        # اگر درخواست Ajax بود → فقط partial برگردان
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(
                self.request,
                "bookmanager/partials/books_list_content.html",
                context
            )

        # در غیر این صورت → صفحه کامل
        return super().render_to_response(context, **response_kwargs)


class BookDetailView(DetailView):
    model = Book
    template_name = "bookmanager/book_details.html"
    context_object_name = "book"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data()

        # اگر درخواست AJAX بود فقط کامنت‌ها را برگردان
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(
                "bookmanager/partials/comments_list.html",
                context,
                request=request
            )
            return JsonResponse({"html": html})

        return self.render_to_response(context)

    def get_queryset(self):
        return Book.objects.prefetch_related(
            Prefetch(
                "comments",
                queryset=Comment.objects.filter(is_active=True)
                .select_related("user")
                .order_by("-created_at"),
                to_attr="approved_comments"
            ),
        )

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        logger.info(f"Fetching book detail page for slug: {slug}")

        return get_object_or_404(
            queryset or self.get_queryset(),
            slug=slug
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments = getattr(self.object, "approved_comments", [])

        paginator = Paginator(comments, 7)
        page_number = self.request.GET.get("page")
        comments_page = paginator.get_page(page_number)

        related_books = (
            Book.objects.filter(categories__in=self.object.categories.all())
            .exclude(id=self.object.id)
            .annotate(comments_count=Count("comments", filter=Q(comments__is_active=True)))
            .distinct()
            .order_by("-sell_count")[:8]
        )

        context.update({
            "comments_page": comments_page,
            "form": CommentForm(),
            "related_books": related_books,

        })

        logger.debug(f"Book '{self.object}' loaded with {len(comments)} approved comments.")

        return context

    def post(self, request, *args, **kwargs):
        """ثبت نظر جدید از کاربر"""
        self.object = self.get_object()
        form = CommentForm(
            request.POST,
            initial={"request": request, "content_object": self.object}
        )

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user if request.user.is_authenticated else None
            comment.content_object = self.object
            comment.ip_address = request.META.get("REMOTE_ADDR")
            comment.save()

            messages.success(
                request,
                "نظر شما با موفقیت ثبت شد و پس از بررسی نمایش داده خواهد شد."
            )

            return redirect(reverse("bookmanager:book_detail", kwargs={"slug": self.object.slug}))

        logger.warning(f"Comment form errors: {form.errors}")
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class AuthorListView(ListView):
    model = Author
    template_name = "bookmanager/author_list.html"
    context_object_name = "authors"
    paginate_by = 6

    def get_queryset(self):
        queryset = Author.objects.all().prefetch_related("books")

        # فیلتر ژانر
        genre = self.request.GET.get("genre")
        if genre:
            queryset = queryset.filter(writing_field=genre)

        # جستجو
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(english_name__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        genres = (
            Author.objects.values("writing_field")
            .annotate(total=Count("id"))
            .order_by("writing_field")
        )

        writing_field_map = dict(Author.WritingField.choices)

        for genre in genres:
            genre["label"] = writing_field_map.get(genre["writing_field"], "")

        context["genres"] = genres
        context["current_genre"] = self.request.GET.get("genre", "")
        context["search_query"] = self.request.GET.get("search", "")

        return context

    def render_to_response(self, context, **response_kwargs):
        # اگر درخواست AJAX بود → فقط HTML لیست + pagination را برگردان
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(
                "bookmanager/partials/author_list_items.html",
                context,
                request=self.request
            )
            pagination = render_to_string(
                "bookmanager/partials/author_pagination.html",
                context,
                request=self.request
            )

            return JsonResponse({
                "html": html,
                "pagination": pagination,
            })

        return super().render_to_response(context, **response_kwargs)


class AuthorDetailView(DetailView):
    model = Author
    template_name = "bookmanager/author_details.html"
    context_object_name = "author"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data()

        # اگر درخواست AJAX بود فقط کامنت‌ها را برگردان
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(
                "bookmanager/partials/comments_list.html",
                context,
                request=request
            )
            return JsonResponse({"html": html})

        return self.render_to_response(context)

    def get_queryset(self):
        return Author.objects.prefetch_related(
            Prefetch(
                "comments",
                queryset=Comment.objects.filter(is_active=True)
                .select_related("user")
                .order_by("-created_at"),
                to_attr="approved_comments"
            ),
            "books"
        )

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        logger.info(f"Fetching author detail page for slug: {slug}")

        return get_object_or_404(
            queryset or self.get_queryset(),
            slug=slug
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments = getattr(self.object, "approved_comments", [])

        paginator = Paginator(comments, 7)
        page_number = self.request.GET.get("page")
        comments_page = paginator.get_page(page_number)

        context.update({
            "comments_page": comments_page,
            "form": CommentForm()
        })

        logger.debug(
            f"Author '{self.object}' loaded with "
            f"{len(comments)} approved comments and "
            f"{self.object.books.count()} books."
        )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        print("posted")
        form = CommentForm(
            request.POST,
            initial={
                "request": request,
                "content_object": self.object
            }
        )
        print("formed ")
        if form.is_valid():
            print("OK")
            comment = form.save(commit=False)
            comment.user = request.user if request.user.is_authenticated else None
            comment.content_object = self.object
            comment.ip_address = request.META.get("REMOTE_ADDR")
            comment.save()

            messages.success(
                request,
                "نظر شما با موفقیت ثبت شد و پس از بررسی نمایش داده خواهد شد."
            )

            return redirect(
                reverse("bookmanager:author_detail", kwargs={"slug": self.object.slug})
            )
        logger.warning(f"Comment form errors: {form.errors}")
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class PublisherListView(ListView):
    model = Publisher
    template_name = "bookmanager/publisher_list.html"
    context_object_name = "publishers"
    paginate_by = 9

    def get_queryset(self):
        return Publisher.objects.all().order_by("name")

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(
                "bookmanager/partials/publisher_list_items.html",
                context,
                request=self.request
            )
            return JsonResponse({"html": html})

        return super().render_to_response(context, **response_kwargs)


class PublisherDetailView(DetailView):
    model = Publisher
    template_name = "bookmanager/publisher_details.html"
    context_object_name = "publisher"

    def get_queryset(self):
        return Publisher.objects.prefetch_related("books")

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        logger.info(f"Fetching publisher detail page for slug: {slug}")

        return get_object_or_404(
            queryset or self.get_queryset(),
            slug=slug
        )
