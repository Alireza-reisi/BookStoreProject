from django import forms
from django.core.exceptions import ValidationError
from .models import ContactMessage
import re
from captcha.fields import CaptchaField

DANGEROUS_CHARS = r"[<>\/\\{}\[\];:\"'`$%^*=+|&]"


def validate_safe_characters(value, field_name):
    if re.search(DANGEROUS_CHARS, value):
        raise ValidationError(f"فیلد {field_name} دارای کاراکترهای غیرمجاز است.")


class ContactForm(forms.ModelForm):
    captcha = CaptchaField(label="کد امنیتی")

    class Meta:
        model = ContactMessage
        fields = ["message", "name", "email", "subject", "captcha"]

        widgets = {
            "message": forms.Textarea(attrs={"class": "form-control w-100", "placeholder": "متن پیام", "rows": 9}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "نام و نام خانوادگی"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "ایمیل"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "موضوع"}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()

        if not name:
            raise ValidationError("نام را وارد کنید.")

        validate_safe_characters(name, "نام")

        # اجازه فقط فارسی، انگلیسی و فاصله
        if not re.match(r"^[\u0600-\u06FFa-zA-Z\s\-\.]+$", name):
            raise ValidationError("نام فقط می‌تواند شامل حروف و فاصله باشد.")

        return name

    def clean_subject(self):
        subject = self.cleaned_data.get("subject", "").strip()

        if not subject:
            raise ValidationError("موضوع پیام را وارد کنید.")

        validate_safe_characters(subject, "موضوع")

        return subject

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()

        if not email:
            raise ValidationError("ایمیل را وارد کنید.")

        validate_safe_characters(email, "ایمیل")

        from django.core.validators import validate_email
        validate_email(email)

        return email

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()

        if not message:
            raise ValidationError("متن پیام را وارد کنید.")

        validate_safe_characters(message, "متن پیام")

        if len(message) < 10:
            raise ValidationError("متن پیام خیلی کوتاه است.")

        return message

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
