"""Views for Home app

The views here will handle requests that are routed to the home
"""
from django.views.generic import TemplateView


# Home Page View
class IndexView(TemplateView):

    template_name = 'frontend/index.html'
