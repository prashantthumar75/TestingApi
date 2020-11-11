from django.urls import path, include
from . import views


urlpatterns=[
    path("add/", views.Student.as_view()),
    path("", views.StudentGet.as_view()),
]