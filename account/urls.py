from django.urls import path
from .views import OTPSendCodeView, OTPVerifyCodeView

app_name = 'account'

urlpatterns = [
    path('otp/send', OTPSendCodeView.as_view(), name='otp_send_code'),
    path('otp/verify', OTPVerifyCodeView.as_view(), name='otp_verify_code'),
]
