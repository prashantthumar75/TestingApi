from django.urls import path, include
from . import views

urlpatterns=[
    path("", views.ClassViewSet.as_view()),
]