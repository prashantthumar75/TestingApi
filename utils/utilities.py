from rest_framework import status
from django.db.models import Q
from rest_framework.response import Response
from departments import models as departments_models
from teachers import models as teachers_models
from organizations import models as organizations_models

def pop_from_data(pop_list, data):
    for _ in pop_list:
        if _ in data:
            data.pop(_)
    return data

def validate_user_type(user_type: str, organization:organizations_models.Organization, user):
    if user_type == "org":
        if organization.user != user:
            return False
        return True
    
    if user_type == "dept":
        departments = departments_models.Department.objects.filter(Q(organization=organization) & Q(user=user) & Q(is_active=True))
        if not len(departments):
            return False
        return True
    
    if user_type == "teacher":
        teachers = teachers_models.Teacher.objects.filter(Q(organization=organization) & Q(user=user) & Q(is_active=True))
        if not len(teachers):
            return False
        return True

    return False
