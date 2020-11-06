from django.urls import path, include
from . import views


urlpatterns=[
    path("join/", views.JoinDepartment.as_view())
]