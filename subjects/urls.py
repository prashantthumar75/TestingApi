from django.urls import path, include
from . import views

urlpatterns=[
    path("add/", views.CreateSubject.as_view()),
    path("", views.Subject.as_view()),
]