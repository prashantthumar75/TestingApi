from django.urls import path, include
from . import views


urlpatterns=[
    path("requests/department/", views.JoinRequestsDepartment.as_view()),
    path("requests/teacher/", views.JoinRequestsTeacher.as_view()),
    path("requests/student/", views.JoinRequestsStudent.as_view()),
]