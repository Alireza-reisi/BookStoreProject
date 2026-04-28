from django import forms
from django.contrib.contenttypes.models import ContentType
from .models import Comment, Book, Author
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
import re
import html
from captcha.fields import CaptchaField


class CommentAdminForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # فقط مدل‌های مجاز
        allowed_models = [Book, Author]

        # contenttype های مجاز
        allowed_cts = ContentType.objects.get_for_models(*allowed_models)

        # محدود کردن queryset
        self.fields["content_type"].queryset = ContentType.objects.filter(
            id__in=[ct.id for ct in allowed_cts.values()]
        )


class CommentForm(forms.ModelForm):
    captcha = CaptchaField(label="کد امنیتی")

    class Meta:
        model = Comment
        fields = ["text", "captcha"]
        widgets = {
            "text": forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                "placeholder": "نظر خود را بنویسید...",
                "maxlength": 2000
            }),
        }

    SPAM_WORDS = [
        # English spam/promo
        "buy now", "click here", "http://spam", "visit my page",
        "earn money", "cheap offer", "casino", "porn", "sex",
        # Persian spam
        "کلیک کن", "خرید کنید", "پولدار شو", "بت", "قمار",
        # Persian profanity (نمونه، می‌توانی لیست کامل‌تری جایگزین کنی)
        "حرامزاده", "کثافت", "احمق", "لعنتی", "گاو", "بی‌شعور", "جاکش", "کونی",
        "گوه", "گند", "پفیوز", "حرامی", "عوضی", "مادر...", "پدر...", "خار...",
    ]

    DANGEROUS_PATTERN = re.compile(
        r"[<>;/{}[\]`$]|--|\b(SELECT|UPDATE|DELETE|INSERT|DROP|ALTER|SCRIPT)\b",
        flags=re.IGNORECASE
    )

    def clean_text(self):
        text = self.cleaned_data.get("text", "").strip()

        if not text:
            raise ValidationError("متن نظر نمی‌تواند خالی باشد.")

        if len(text) < 5:
            raise ValidationError("نظر باید حداقل ۵ کاراکتر باشد.")
        if len(text) > 2000:
            raise ValidationError("حداکثر طول متن ۲۰۰۰ کاراکتر است.")

        text_unescaped = html.unescape(text)

        if self.DANGEROUS_PATTERN.search(text_unescaped):
            raise ValidationError("متن حاوی کاراکتر یا کد غیرمجاز است.")

        if re.search(r"<.*?>", text_unescaped):
            raise ValidationError("ارسال تگ HTML در متن مجاز نیست.")

        lowered = text_unescaped.lower()
        for bad_word in self.SPAM_WORDS:
            if bad_word in lowered:
                raise ValidationError("متن نظر شامل واژه نامناسب یا تبلیغاتی است.")

        if lowered.count("http://") + lowered.count("https://") > 2:
            raise ValidationError("تعداد لینک‌های استفاده‌شده بیش از حد مجاز است.")

        if re.search(r"(.)\1{7,}", text_unescaped):
            raise ValidationError("از تکرار زیاد کاراکترها خودداری کنید.")

        return text_unescaped

    def clean(self):
        cleaned = super().clean()
        request = self.initial.get("request")
        content_object = self.initial.get("content_object")
        text = cleaned.get("text")

        if not text or not request or not content_object:
            return cleaned

        user = request.user if request.user.is_authenticated else None
        ip = getattr(request, "META", {}).get("REMOTE_ADDR")

        query = Comment.objects.filter(
            text=text,
            content_type__model=content_object._meta.model_name,
            object_id=content_object.pk,
        )

        if user:
            query = query.filter(user=user)
        else:
            query = query.filter(ip_address=ip) if "ip_address" in [f.name for f in Comment._meta.fields] else query

        if query.exists():
            raise ValidationError("این نظر قبلاً ثبت شده است یا تکراری است.")

        # محدودیت زمانی بین دو نظر (anti-flood)
        if user:
            last_comment = Comment.objects.filter(user=user).order_by("-created_at").first()
            if last_comment and (timezone.now() - last_comment.created_at).total_seconds() < 20:
                raise ValidationError("لطفاً کمی صبر کرده و سپس نظر ارسال کنید.")

        return cleaned


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["name", "english_name", "photo", "biography"]
        error_messages = {
            "name": {"blank": "نام نویسنده نمی‌تواند خالی باشد"},
            "english_name": {"blank": "نام انگلیسی نویسنده اجباری است"},
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise ValidationError("نام باید حداقل ۲ کاراکتر باشد.")
        return name

    def clean_english_name(self):
        english = self.cleaned_data["english_name"].strip()
        if not english.replace(" ", "").isalpha():
            raise ValidationError("نام انگلیسی فقط باید حرف باشد.")
        return english

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo:
            if photo.size > 2 * 1024 * 1024:  # 2MB
                raise ValidationError("حجم عکس نباید بیشتر از ۲ مگابایت باشد.")
            if not photo.content_type.startswith("image/"):
                raise ValidationError("فایل انتخاب‌شده تصویر نیست.")
        return photo
