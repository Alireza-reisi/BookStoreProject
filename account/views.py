from django.shortcuts import redirect
from django.views.generic import FormView
from django.urls import reverse_lazy, reverse
from .forms import OTPSendCodeForm, OTPVerifyCodeForm
from django.contrib import messages
from django.contrib.auth import login


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
