from django.urls import path, include
from . import views


urlpatterns=[
    path("verify-dept_id/", views.VerifyDeptId.as_view()),
    path("assigned-classes/", views.AssignedClass.as_view()),
    path("join/", views.JoinDepartment.as_view()),
    path("", views.Department.as_view()),
]