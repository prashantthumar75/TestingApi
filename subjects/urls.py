from django.urls import path, include
from . import views

urlpatterns=[
    path("", views.CreateSubject.as_view()),
]