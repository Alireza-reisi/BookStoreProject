from Lib.django.views.generic.base import TemplateView

from django.shortcuts import render


class HomeView(TemplateView):
    template_name = 'bookmanager/home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
