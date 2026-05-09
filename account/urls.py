from django.urls import path
from .views import OTPSendCodeView, OTPVerifyCodeView, ProfileView, ProfileSectionView

app_name = 'account'

urlpatterns = [
    path('otp/send', OTPSendCodeView.as_view(), name='otp_send_code'),
    path('otp/verify', OTPVerifyCodeView.as_view(), name='otp_verify_code'),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/info", ProfileSectionView.as_view(), name="profile_info_section",)
]
