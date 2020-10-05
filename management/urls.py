from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views
from . import apis

app_name = 'management'

extra_urls = [
    path('terms-and-conditions/', apis.TermsAndConditionsApi.as_view()),
]

urlpatterns = [

    # api urls
    path('api/', include(extra_urls))
]
