from django.urls import path

from proxy.fc import views as fc_views
from proxy.fi import views as fi_views

urlpatterns = [
    path("", fc_views.fc_callback),
    path("ami-fi-authorize-request/", fi_views.authorize_request),
    path("ami-fi-get-from-url", fi_views.get_from_url),
    path("api/v1/fi/authorize/", fi_views.authorize),
]
