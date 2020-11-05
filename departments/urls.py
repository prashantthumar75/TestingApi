from django.urls import path, include
from . import views


urlpatterns=[
    path("create/", views.Department.as_view())
]