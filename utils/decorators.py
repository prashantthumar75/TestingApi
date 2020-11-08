from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from organizations import models as organizations_models
from departments import models as departments_models


def validate_org(func):
    def check(*args, **kwargs):

        request = args[1]

        if request.method == "GET":
            org_id = request.query_params.get('org_id', 0)
        else:
            org_id = request.data.get('org_id', 0)

        if not org_id:
            return Response({'details': ['org_id is not passed']}, status.HTTP_400_BAD_REQUEST)

        organizations = organizations_models.Organization.objects.filter(Q(org_id=org_id) & Q(is_active=True))

        if not len(organizations):
            return Response({'details': ['Invalid org_id']}, status.HTTP_400_BAD_REQUEST)

        kwargs.update({"organization": organizations[0]})

        return func(*args, **kwargs)
        
    return check


def validate_dept(func):
    def check(*args, **kwargs):

        request = args[1]

        if request.method == "GET":
            dept_id = request.query_params.get('dept_id', 0)
        else:
            dept_id = request.data.get('dept_id', 0)

        if not dept_id:
            return Response({'details': ['dept_id is not passed']}, status.HTTP_400_BAD_REQUEST)

        departments = departments_models.Department.objects.filter(Q(department_id=dept_id) & Q(is_active=True))

        if not len(departments):
            return Response({'details': ['Invalid dept_id']}, status.HTTP_400_BAD_REQUEST)

        kwargs.update({"department": departments[0]})

        return func(*args, **kwargs)
        
    return check


def is_organization(func):
    @validate_org
    def check(*args, **kwargs):

        request = args[1]
        user = request.user
        organization = kwargs.get("organization")

        if organization.user == user:
            return func(*args, **kwargs)
        
        return Response({'details': ['Invalid org_id']}, status.HTTP_400_BAD_REQUEST)

    return check



def is_department(func):
    @validate_dept
    @validate_org
    def check(*args, **kwargs):

        request = args[1]
        user = request.user

        organization = kwargs.get('organization')

        department = kwargs.get('department')
        
        if department.user == user and department.organization == organization:
            return func(*args, **kwargs)
        
        return Response({'details': ['Invalid dept_id']}, status.HTTP_400_BAD_REQUEST)

    return check