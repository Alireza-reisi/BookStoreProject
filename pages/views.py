import logging
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ContactForm
from bookmanager.models import Author, Publisher, Book
from django.db.models import Count
from django.core.cache import cache


logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        best_authors = cache.get('home_best_authors')
        if best_authors is None:
            best_authors = (
                Author.objects
                .annotate(books_count=Count('books'))
                .order_by('-books_count')[:4]
            )
            cache.set('home_best_authors', best_authors, 60 * 60)

        best_publishers = cache.get('home_best_publishers')
        if best_publishers is None:
            best_publishers = (
                Publisher.objects
                .annotate(books_count=Count('books'))
                .order_by('-books_count')[:8]
            )
            cache.set('home_best_publishers', best_publishers, 60 * 60)

        most_sales_books = cache.get('home_most_sales_books')
        if most_sales_books is None:
            most_sales_books = (
                Book.objects
                .order_by('-sell_count')[:10]
            )
            cache.set('home_most_sales_books', most_sales_books, 60 * 60)

        new_books = cache.get('home_new_books')
        if new_books is None:
            new_books = (
                Book.objects
                .order_by('-created_at')[:6]
            )
            cache.set('home_new_books', new_books, 60 * 60)

        context['best_authors'] = best_authors
        context['best_publishers'] = best_publishers
        context['most_sales_books'] = most_sales_books
        context['new_books'] = new_books

        return context


class AboutView(TemplateView):
    template_name = "pages/about.html"


class ContactView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("pages:contactus")

    def form_valid(self, form):
        instance = form.save()
        ip = self.request.META.get("REMOTE_ADDR")
        logger.info(
            "New contact message received | name=%s email=%s subject=%s ip=%s",
            instance.name,
            instance.email,
            instance.subject,
            ip,
        )
        messages.success(
            self.request,
            "پیام شما با موفقیت دریافت شد. در صورت نیاز با شما ارتباط برقرار خواهیم کرد."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            "Invalid contact form submission | errors=%s ip=%s",
            form.errors,
            self.request.META.get("REMOTE_ADDR"),
        )
        return super().form_invalid(form)
