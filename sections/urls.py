from django.urls import path, include
from . import views

urlpatterns=[
    path("add/", views.CreateSection.as_view()),
    path("", views.Section.as_view()),
]