from django.urls import path, include
from . import views

urlpatterns=[
    path("event/", views.Event.as_view()),
    path("assignments/files/", views.AssignmentFile.as_view()),
    path("assignments/", views.Assignment.as_view()),
    path("submitted-assignments/", views.SubmittedAssignment.as_view()),
    path("submitted-assignments/files/", views.SubmittedAssignmentFile.as_view()),
]