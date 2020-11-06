from django.urls import path, include
from . import views


urlpatterns=[
    path("join/", views.JoinDepartment.as_view()),
    path("assigned-classes/", views.AssignedClass.as_view())
]