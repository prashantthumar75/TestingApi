from django.urls import path, include
from . import views

urlpatterns=[
    path("organization/", views.OrganizationAnnouncenment.as_view()),
]