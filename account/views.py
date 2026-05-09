from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, UpdateView
from django.urls import reverse_lazy, reverse
from .forms import OTPSendCodeForm, OTPVerifyCodeForm, ProfileForm
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash

User = get_user_model()


# ------------------------------------------
# --------- OTP login/signup views ---------
# ------------------------------------------

class OTPSendCodeView(FormView):
    template_name = 'account/send_otp.html'
    form_class = OTPSendCodeForm
    success_url = reverse_lazy('account:otp_verify_code')

    def form_valid(self, form):
        otp_instance = form.save()

        # محل قرار دادن کد ارسال پیامک
        print(f"کد تایید برای {otp_instance.phone} = {otp_instance.verification_code}")

        self.request.session['user_phone'] = otp_instance.phone

        messages.success(self.request, "کد تأیید برای شما ارسال شد.")
        return super().form_valid(form)


class OTPVerifyCodeView(FormView):
    template_name = 'account/verify_code.html'
    form_class = OTPVerifyCodeForm
    success_url = reverse_lazy('pages:home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        phone = self.request.session.get('user_phone')
        if not phone:
            return redirect(reverse('account:otp_send_code'))

        kwargs['phone'] = phone
        return kwargs

    def form_valid(self, form):
        user = form.get_or_create_user()

        login(self.request, user)

        if user.has_usable_password():
            messages.success(self.request, "با موفقیت وارد شدید.")
        else:
            messages.success(
                self.request,
                "با موفقیت وارد شدید. می‌توانید رمز عبور خود را از پروفایل تنظیم کنید."
            )

        self.request.session.pop('user_phone', None)

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)


# ------------------------------------------
# --------- phone-pass login views ---------
# ------------------------------------------


# ------------------------------------------
# ----------- User profile views -----------
# ------------------------------------------

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "account/profile.html"


class ProfileSectionView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "account/panel_sections/personal_info.html"
    success_url = reverse_lazy("account:profile")

    def get_object(self, queryset=None):
        """بازگرداندن کاربر جاری برای نمایش اطلاعات پروفایل"""
        return self.request.user

    def get_form_kwargs(self):
        """
        اطمینان حاصل می‌کند که هنگام دریافت GET اولیه، کپچا خنثی باشد
        (چون کپچا فقط در حالت ویرایش نمایش داده می‌شود).
        """
        kwargs = super().get_form_kwargs()
        if self.request.method == "GET":
            # کپچا را حذف یا خنثی کن تا در نمایش اولیه اجباری نباشد
            kwargs["initial"] = kwargs.get("initial", {})
            kwargs["initial"]["captcha"] = None
        return kwargs

    def form_valid(self, form):
        """
        ذخیره‌ی اطلاعات کاربر + مدیریت تغییر رمز عبور
        """
        response = super().form_valid(form)
        password = form.cleaned_data.get("password")

        if password:
            # اگر رمز وارد شده بود، رمز را تغییر بده و session را به‌روز کن
            self.object.set_password(password)
            self.object.save()
            update_session_auth_hash(self.request, self.object)
        else:
            # اگر رمز خالی بود، فرم خطای خاصی نده و فیلدها را پاک کن
            form.cleaned_data["password"] = ""
            form.cleaned_data["password2"] = ""

        messages.success(self.request, "اطلاعات حساب کاربری با موفقیت ذخیره شد.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "خطا در ذخیره اطلاعات. لطفاً فرم را بررسی کنید.")
        return super().form_invalid(form)
