from django.urls import path, include
from . import views


urlpatterns=[
    path("create/", views.Teacher.as_view())
]