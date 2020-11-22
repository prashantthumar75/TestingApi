from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.db.models import Q

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi

# CUSTOM
from . import models, serializers
from teachers import models as teachers_models
from departments import serializers as departments_serializers
from departments import models as departments_models
from students import models as student_models
from sections import models as section_models
from students import serializers as student_serializers
from sections import serializers as section_serializers
from teachers import serializers as teachers_serializers
from users import models as users_models
from utils.decorators import is_organization, validate_org, validate_dept

# Utils
import json
from utils.decorators import is_organization, validate_org
from utils.utilities import pop_from_data

class Organization(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.OrganizationSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response(
                "Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    @is_organization
    def get(self, request, **kwargs):
        query_params = self.request.query_params

        organization = kwargs.get('organization')

        org_id = organization.id
        qs = models.Organization.objects.filter(id=org_id, is_active=True)

        serializer = serializers.OrganizationSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            title="Update Organization",
            type=openapi.TYPE_OBJECT,
            properties={
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'join_id': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'contact_name': openapi.Schema(type=openapi.TYPE_STRING),
                'contact_phone': openapi.Schema(type=openapi.TYPE_STRING),
                'contact_email': openapi.Schema(type=openapi.TYPE_STRING),
                'location': openapi.Schema(type=openapi.TYPE_STRING),
                'accepting_req': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            }
        ),
         manual_parameters=[
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response("OK- Successful POST Request"),
            401: openapi.Response(
                "Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            422: openapi.Response("Unprocessable Entity- Make sure that all the required field values are passed"),
            500: openapi.Response("Internal Server Error- Error while processing the POST Request Function.")
        }
    )
    @is_organization
    def put(self, request, *args, **kwargs):
        query_params = self.request.query_params

        data = request.data

        data = pop_from_data(["is_active", "user"], data)
        organization = kwargs.get("organization")

        serializer = serializers.OrganizationSerializer(organization, data=data, partial=True)

        if not serializer.is_valid():
            return Response({'details': [str(serializer.errors)]}, status.HTTP_400_BAD_REQUEST)

        serializer.save()
        msgs = [
            'successfully updated department'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)


class VerifyOrgId(views.APIView):

    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    @validate_org
    def get(self, request, *args, **kwargs):
        serializer = serializers.OrganizationSerializer(kwargs.get("organization"))
        return Response(serializer.data, status.HTTP_200_OK)


class JoinRequestsDepartment(views.APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    @is_organization
    def get(self, request, *args, **kwargs): 

        departments = departments_models.Department.objects.filter(
            Q(organization=kwargs.get("organization")) & Q(is_active=True))

        serializer = departments_serializers.DepartmentSerializer(departments, many=True)

        return Response(serializer.data, status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Join department request",
            type=openapi.TYPE_OBJECT,
            properties={
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'dept_id': openapi.Schema(type=openapi.TYPE_STRING),
                'requesting_user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={
            200: openapi.Response("OK- Successful POST Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            422: openapi.Response("Unprocessable Entity- Make sure that all the required field values are passed"),
            500: openapi.Response("Internal Server Error- Error while processing the POST Request Function.")
        }
    )
    @validate_dept
    @is_organization
    def post(self, request, *args, **kwargs):
        data = request.data
        requesting_user_id = data.get("requesting_user_id", 0)

        if not requesting_user_id:
            errors = [
                'requesting_user_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        organization = kwargs.get("organization")
        department = kwargs.get("department")

        if not department.organization == organization:
            errors = [
                'Invalid dept_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        request_list = []
        for i in department.requesting_users.all():
            request_list.append(str(i.id))

        if not str(requesting_user_id) in request_list:
            errors = [
                'Invalid requesting_user_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        department.requesting_users.remove(int(requesting_user_id))
        department.user = users_models.User.objects.get(id=int(requesting_user_id))
        department.save()

        msgs = [
            'Request accepted successfully'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)


class JoinRequestsTeacher(views.APIView):
    queryset = models.Organization.objects.filter(is_active=True)

    serializer_class = teachers_serializers.TeacherSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    @is_organization
    def get(self, request, **kwargs):
        query_params = self.request.query_params

        organizations=kwargs.get("organization")

        teachers = teachers_models.Teacher.objects.filter(
            Q(requested_organization__id=organizations.id) & Q(is_active=True))

        serializer = teachers_serializers.TeacherSerializer(teachers, many=True)

        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Join teacher request",
            type=openapi.TYPE_OBJECT,
            properties={
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'teachers': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response("OK- Successful POST Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            422: openapi.Response("Unprocessable Entity- Make sure that all the required field values are passed"),
            500: openapi.Response("Internal Server Error- Error while processing the POST Request Function.")
        }
    )

    def post(self, request):
        data = request.data
        org_id = data.get('org_id',"")
        teachers = str(data.get("teachers", "[]"))

        if not org_id:
            errors = [
                'org_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        organizations = self.queryset.filter(Q(user__id=request.user.id) & Q(org_id=org_id))

        if not len(organizations):
            errors = [
                'Invalid org_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if len(teachers) < 3:
            errors = [
                "teachers not passed or teachers format should be like this. [1, 2, 3] where 1, 2 and 3 are teacher ID's"
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        try:
            teachers = teachers.replace(" ", "")
            teachers = teachers[1:len(teachers) - 1].split(",")
            teachers = [int(i) for i in teachers]
        except Exception as e:
            errors = [
                "teachers format should be like this. [1, 2, 3] where 1, 2 and 3 are teacher ID's",
                str(e)
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        teach_qs = teachers_models.Teacher.objects.filter(is_active=True)

        valid_teachers = []

        for i in teachers:
            temp_teach = teach_qs.filter(id=i)
            if not len(temp_teach):
                errors = [
                    'Invalid teacher ID'
                ]
                return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
            temp_teach = temp_teach[0]
            if not temp_teach.requested_organization or temp_teach.requested_organization.user.id != request.user.id:
                errors = [
                    'already accepted requests'
                ]
                return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
            valid_teachers.append(temp_teach)

        for temp_teach in valid_teachers:
            temp_teach.organization = temp_teach.requested_organization
            temp_teach.requested_organization = None
            temp_teach.save()

        return Response({"details": ["Successfully accepted all provided requests."]}, status.HTTP_200_OK)


class JoinRequestsStudent(views.APIView):

    serializer_class = student_serializers.StudentSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
            openapi.Parameter(name="sec_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    @is_organization
    def get(self, request, **kwargs):
        query_params = self.request.query_params
        sec_id = query_params.get('sec_id',None)

        org = kwargs.get('organization')
        if not sec_id:
            errors = [
                'sec_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        students = student_models.Student.objects.filter(
            Q(requested_section__id = sec_id) & Q(is_active=True)& Q(requested_section__of_class__department__organization__org_id=org.org_id)
        )

        if not len(students):
            errors = [
                f'no request pending for this section_id: {sec_id}'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        serializer = student_serializers.StudentSerializer(students, many=True)

        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Join student request",
            type=openapi.TYPE_OBJECT,
            properties={
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'students': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response("OK- Successful POST Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            422: openapi.Response("Unprocessable Entity- Make sure that all the required field values are passed"),
            500: openapi.Response("Internal Server Error- Error while processing the POST Request Function.")
        }
    )
    @is_organization
    def post(self, request, **kwargs):
        data = request.data
        students = str(data.get("students", "[]"))

        org = kwargs.get('organization')

        if len(students) < 3:
            errors = [
                "students not passed or students format should be like this. [1, 2, 3] where 1, 2 and 3 are student ID's"
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        organizations = models.Organization.objects.filter(Q(user__id=request.user.id) & Q(org_id=org.org_id))

        if not len(organizations):
            errors = [
                'Invalid org_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        try:
            students = students.replace(" ", "")
            students = students[1:len(students) - 1].split(",")
            students = [int(i) for i in students]
        except Exception as e:
            errors = [
                "students format should be like this. [1, 2, 3] where 1, 2 and 3 are student ID's",
                str(e)
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        stud_qs = student_models.Student.objects.filter(Q(is_active=True) & Q(requested_section__of_class__department__organization__org_id=org.org_id))

        if not stud_qs:
            for i in students:
                stud_ = student_models.Student.objects.filter(
                    Q(is_active=True)& Q(id=i) & Q(requested_section=None)&Q(section__of_class__department__organization__org_id=org.org_id))
                if stud_:
                    errors = [
                        "already accepted requests"
                    ]
                    return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

            errors = [
                "invalid organization request"
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        valid_students = []

        for i in students:
            temp_stud = stud_qs.filter(id=i)
            if not len(temp_stud):
                errors = [
                    'Invalid student ID'
                ]
                return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
            temp_stud = temp_stud[0]
            if not temp_stud.requested_section:
                errors = [
                    'no students in waiting list'
                ]
                return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
            valid_students.append(temp_stud)

        for temp_stud in valid_students:
            temp_stud.section = temp_stud.requested_section
            temp_stud.requested_section = None
            temp_stud.save()

        return Response({"details": ["Successfully accepted all provided requests."]}, status.HTTP_200_OK)
