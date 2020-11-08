from django.urls import path, include
from . import views

urlpatterns=[
    path("daily-class/", views.DailyClass.as_view()),
]