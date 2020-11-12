from django.urls import path, include
from . import views

urlpatterns=[
    path("assign-teacher/", views.AssignTeacher.as_view()),
    path("", views.CreateSection.as_view()),
]