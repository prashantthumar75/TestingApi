from rest_framework import status
from django.db.models import Q
from rest_framework.response import Response
from departments import models as departments_models
from classes import models as class_models
from subjects import models as subjects_models
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


def validate_from(user_type: str, organization:organizations_models.Organization, user, From:int):
    if user_type == "org":
        if organization.user != user:
            return False
        return organization.user

    if user_type == "dept":
        departments = departments_models.Department.objects.filter(Q(organization=organization) & Q(user=user) & Q(is_active=True))
        if not len(departments):
            return False
        department = departments[0]
        classes = class_models.Class.objects.filter(Q(id=From) & Q(department=department)& Q(is_active=True))
        if not len(classes):
            return False
        cls = classes[0]
        if From == cls.id:
            return cls
        else:
            return False

    if user_type == "teacher":
        teachers = teachers_models.Teacher.objects.filter(Q(organization=organization) & Q(user=user) & Q(is_active=True))
        if not len(teachers):
            return False
        teacher = teachers[0]
        subjects = subjects_models.Subject.objects.filter(Q(id=From) & Q(teachers=teacher) & Q(is_active=True))
        if not len(subjects):
            return False
        subject = subjects[0]
        if From == subject.id:
            return subject
        else:
            return False

    return False
# Token d6c6ab0e79e3901d398b2358f260f14d8bc69376