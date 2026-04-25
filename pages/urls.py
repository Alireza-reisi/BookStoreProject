from django.urls import path
from .views import HomeView, AboutView, ContactView

app_name = 'pages'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about-us/', AboutView.as_view(), name='aboutus'),
    path('contact-us/', ContactView.as_view(), name='contactus'),

]
