from django.conf.urls import include, url
from app.views import TestView

urlpatterns = [
    url(r'^test/$', TestView.as_view()),
    ]
