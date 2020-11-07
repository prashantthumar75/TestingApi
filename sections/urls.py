from django.urls import path, include
from . import views

urlpatterns=[
    path("assign-teacher/", views.AssignTeacher.as_view()),
    path("add/", views.CreateSection.as_view()),
    path("", views.Section.as_view()),
]