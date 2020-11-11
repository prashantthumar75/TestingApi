from django.urls import path, include
from . import views


urlpatterns=[
    path("assign-subject/", views.AssignSubject.as_view()),
    path("add/", views.Teacher.as_view()),
]