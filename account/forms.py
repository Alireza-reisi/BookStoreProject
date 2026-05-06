from django import forms
from django.contrib.auth import get_user_model
from .models import OTP
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
import random
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


# ------------------------------------------
# ------- customize User model forms -------
# ------------------------------------------

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تکرار رمز عبور', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["phone", "is_admin", 'is_superuser']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")

        return password2


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["phone", "password", "is_active", "is_admin", 'is_superuser']


# ------------------------------------------
# --------- OTP login/signup forms ---------
# ------------------------------------------
class OTPSendCodeForm(forms.Form):
    phone = forms.CharField(
        label='شماره موبایل',
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثال: 09123456789',
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()

        if not phone:
            raise ValidationError("شماره تلفن الزامی است.")

        if not phone.isdigit():
            raise ValidationError("شماره تلفن باید فقط شامل عدد باشد.")

        if len(phone) != 11:
            raise ValidationError("طول شماره تلفن نامعتبر است.")

        return phone

    def save(self):
        phone = self.cleaned_data['phone']
        generated_code = str(random.randint(100000, 999999))

        otp_obj, created = OTP.objects.update_or_create(
            phone=phone,
            defaults={
                'verification_code': generated_code
            }
        )

        return otp_obj


class OTPVerifyCodeForm(forms.Form):
    verification_code = forms.CharField(
        label='کد تأیید',
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'کد ۶ رقمی'
        })
    )

    def __init__(self, *args, **kwargs):
        self.phone = kwargs.pop('phone', None)
        if not self.phone:
            raise ValueError("شماره موبایل باید برای ارسال کد تایید وارد شده باشد.")

        super().__init__(*args, **kwargs)

    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code')

        if not code:
            raise ValidationError("وارد کردن کد تأیید الزامی است.")

        if not code.isdigit():
            raise ValidationError("کد تأیید باید فقط شامل ارقام باشد.")

        if len(code) != 6:
            raise ValidationError("کد تأیید باید ۶ رقم باشد.")

        try:
            otp_obj = OTP.objects.get(phone=self.phone)
        except OTP.DoesNotExist:
            raise ValidationError(
                "کد تأیید برای این شماره ارسال نشده یا منقضی شده است."
            )

        if timezone.now() > otp_obj.update_time + timedelta(minutes=3):
            otp_obj.delete()
            raise ValidationError("زمان استفاده از کد تأیید به پایان رسیده است.")

        if otp_obj.verification_code != code:
            raise ValidationError("کد تأیید اشتباه است.")

        otp_obj.delete()

        return code

    def get_or_create_user(self):
        user, created = User.objects.get_or_create(phone=self.phone)

        if created:
            user.set_unusable_password()
            user.save()

        return user
