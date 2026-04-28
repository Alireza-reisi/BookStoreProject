from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Book, Author, Publisher, Category, Comment, CommentReaction
from django.db.models import Prefetch
from .forms import AuthorForm, CommentForm
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.urls import reverse
from django.contrib import messages
import logging
from django.template.loader import render_to_string
from django.http import JsonResponse

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


class AuthorDetailView(DetailView):
    model = Author
    template_name = "bookmanager/author-details.html"
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
        print(f" error : {form.errors}")
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)
