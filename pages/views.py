import logging

from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import ContactForm

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "pages/home.html"


class AboutView(TemplateView):
    template_name = "pages/about.html"


class ContactView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("pages:contactus")

    def form_valid(self, form):
        instance = form.save()

        ip = self.request.META.get("REMOTE_ADDR")
        user_agent = self.request.META.get("HTTP_USER_AGENT")
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
