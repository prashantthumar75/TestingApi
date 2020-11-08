from django.urls import path, include
from . import views

urlpatterns=[
    path("daily-class/", views.Event.as_view()),
    path("assignments/", views.Assignment.as_view()),
]