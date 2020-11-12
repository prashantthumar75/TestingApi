from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from organizations import models as organizations_models
from departments import models as departments_models
from teachers import models as teachers_models
from students import models as students_models
from events import models as events_models


##############################################
#               Validate Objects             #
##############################################
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


def validate_event(func):
    def check(*args, **kwargs):

        request = args[1]

        if request.method == "GET":
            event_id = request.query_params.get('event', 0)
        else:
            event_id = request.data.get('event', 0)

        if not event_id:
            return Response({'details': ['event is not passed']}, status.HTTP_400_BAD_REQUEST)

        events = events_models.Event.objects.filter(Q(id=event_id) & Q(is_active=True))

        if not len(events):
            return Response({'details': ['Invalid event']}, status.HTTP_400_BAD_REQUEST)

        kwargs.update({"event": events[0]})

        return func(*args, **kwargs)
        
    return check


def validate_assignment(func):
    def check(*args, **kwargs):

        request = args[1]

        if request.method == "GET":
            assignment_id = request.query_params.get('assignment', 0)
        else:
            assignment_id = request.data.get('assignment', 0)

        if not assignment_id:
            return Response({'details': ['assignment is not passed']}, status.HTTP_400_BAD_REQUEST)

        assignments = events_models.Assignment.objects.filter(Q(id=assignment_id) & Q(is_active=True))

        if not len(assignments):
            return Response({'details': ['Invalid assignment ID']}, status.HTTP_400_BAD_REQUEST)

        kwargs.update({"assignment": assignments[0]})

        return func(*args, **kwargs)
        
    return check


def validate_submitted_assignment(func):
    def check(*args, **kwargs):

        request = args[1]

        if request.method == "GET":
            submitted_assignment_id = request.query_params.get('submitted_assignment', 0)
        else:
            submitted_assignment_id = request.data.get('submitted_assignment', 0)

        if not submitted_assignment_id:
            return Response({'details': ['submitted_assignment is not passed']}, status.HTTP_400_BAD_REQUEST)

        submitted_assignments = events_models.SubmittedAssignment.objects.filter(Q(id=submitted_assignment_id) & Q(is_active=True))

        if not len(submitted_assignments):
            return Response({'details': ['Invalid submitted_assignment ID']}, status.HTTP_400_BAD_REQUEST)

        kwargs.update({"submitted_assignment": submitted_assignments[0]})

        return func(*args, **kwargs)
        
    return check


#############################################
#               Validate Users              #
#############################################

def is_organization(func):
    @validate_org
    def check(*args, **kwargs):

        request = args[1]
        user = request.user
        organization = kwargs.get("organization")

        if organization.user == user:
            return func(*args, **kwargs)
        
        return Response({'details': ['Permission denied, invalid organization']}, status.HTTP_400_BAD_REQUEST)

    return check


def is_department(func):
    @validate_dept
    @validate_org
    def check(*args, **kwargs):

        request = args[1]
        user = request.user

        organization = kwargs.get('organization')

        department = kwargs.get('department')
        
        if department.user == user and department.organization == organization and department.organization == organization:
            return func(*args, **kwargs)
        
        return Response({'details': ['Permission denied, invalid department']}, status.HTTP_400_BAD_REQUEST)

    return check


def is_org_or_department(func):
    @validate_org
    @validate_dept
    def check(*args, **kwargs):

        request = args[1]
        user = request.user

        organization = kwargs.get('organization')
        department = kwargs.get('department')
        
        # Checking whether the user is department or org.
        if department.user == user or organization.user == user:
            return func(*args, **kwargs)

        return Response({'details': ['Permission denied, invalid organization or department']}, status.HTTP_400_BAD_REQUEST)

    return check


def is_teacher(func):
    @validate_org
    def check(*args, **kwargs):

        request = args[1]
        user = request.user

        organization = kwargs.get('organization')

        teachers = teachers_models.Teacher.objects.filter(Q(user=user) & Q(organization=organization) & Q(is_active=True))

        if not len(teachers):
            return Response({'details': ['Permission denied, invalid teacher']}, status.HTTP_400_BAD_REQUEST)

        kwargs.update({"teacher": teachers[0]})
        return func(*args, **kwargs)
        
    return check


def is_student(func):
    @validate_org
    def check(*args, **kwargs):

        request = args[1]
        user = request.user

        organization = kwargs.get('organization')

        students = students_models.Student.objects.filter(Q(user=user) & Q(section__of_class__department__organization=organization) & Q(is_active=True))

        if not len(students):
            return Response({'details': ['Permission denied, invalid student']}, status.HTTP_400_BAD_REQUEST)

        kwargs.update({"student": students[0]})
        return func(*args, **kwargs)
        
    return check