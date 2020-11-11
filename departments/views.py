from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from django.db.models import Q

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi

# Custom
from . import models, serializers
from students import models as student_models
from students import serializers as student_serializers
from classes import models as classes_models
from classes import serializers as classes_serializers
from organizations import models as organizations_models
from organizations import serializers as organizations_serializers


# Utils
import json
from utils.decorators import validate_dept, validate_org, is_department

class VerifyDeptId(views.APIView):

    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="dept_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    @validate_dept
    def get(self, request, *args, **kwargs):
        serializer = serializers.DepartmentSerializer(kwargs.get("department"))
        return Response(serializer.data, status.HTTP_200_OK)

class Department(views.APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="id", in_="query", type=openapi.TYPE_INTEGER),
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        query_params = self.request.query_params
        id = query_params.get('id', None)
        org_id = query_params.get('org_id', None)

        qs = models.Department.objects.filter(is_active=True)

        if id:
            qs = qs.filter(id=int(id))

        if org_id:
            qs = qs.filter(organization__org_id=org_id)

        serializer = serializers.DepartmentSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

class AddDepartment(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DepartmentSerializer

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Join department request",
            type=openapi.TYPE_OBJECT,
            properties={
                'org_join_id': openapi.Schema(type=openapi.TYPE_STRING),
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response("OK- Successful POST Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            422: openapi.Response("Unprocessable Entity- Make sure that all the required field values are passed"),
            500: openapi.Response("Internal Server Error- Error while processing the POST Request Function.")
        }
    )
    @validate_org
    def post(self, request, *args, **kwargs):
        data = json.loads(json.dumps(request.data))
        org_id = kwargs.get("org_id")
        org_join_id = data.get("org_join_id")

        user = request.user
        if not org_join_id:
            errors = [
                'Org_Join_ID  is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        organizations = organizations_models.Organization.objects.filter(join_id=org_join_id)
        if not len(organizations):
            errors = [
                'Invalid organization Join ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        organization = organizations[0]

        if not organization.is_active:
            errors = [
                'Invalid organization Join ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not organization.accepting_req:
            errors = [
                'This organization is currently not accepting requests'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        data.update({
            "organization" : organization.user.id,
            "requesting_users": [user.id]
        })

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            title="Update Department",
            type=openapi.TYPE_OBJECT,
            properties={
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'dept_id': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'contact_name': openapi.Schema(type=openapi.TYPE_STRING),
                'contact_phone': openapi.Schema(type=openapi.TYPE_INTEGER),
                'contact_email': openapi.Schema(type=openapi.TYPE_STRING),
                'department_id': openapi.Schema(type=openapi.TYPE_STRING),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),

            }
        ),
        responses={
            200: openapi.Response("OK- Successful POST Request"),
            401: openapi.Response(
                "Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            422: openapi.Response("Unprocessable Entity- Make sure that all the required field values are passed"),
            500: openapi.Response("Internal Server Error- Error while processing the POST Request Function.")
        }
    )
    @validate_org
    @is_department
    def put(self, request, *args, **kwargs):
        data = request.data
        is_active = data.get('is_active', False)
        name = data.get("name", "")
        contact_name = data.get("contact_name", "")
        department_id = data.get("department_id", "")
        phone = data.get("contact_phone", "")
        email = data.get("contact_email", "")

        data_dict = {
            "name": name,
            "contact_name": contact_name,
            "contact_phone": phone,
            "contact_email": email,
            "department_id": department_id,
            "is_active": is_active,
        }
        department = kwargs.get("department")

        serializer = serializers.DepartmentSerializer(department, data=data_dict, partial=True)

        if not serializer.is_valid():
            return Response({'details': [str(serializer.errors)]}, status.HTTP_400_BAD_REQUEST)

        serializer.save()
        msgs = [
            'successfully updated assignment'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)


class JoinDepartment(views.APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DepartmentSerializer

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Join department request",
            type=openapi.TYPE_OBJECT,
            properties={
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'dept_id': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response("OK- Successful POST Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            422: openapi.Response("Unprocessable Entity- Make sure that all the required field values are passed"),
            500: openapi.Response("Internal Server Error- Error while processing the POST Request Function.")
        }
    )
    @validate_org
    @validate_dept
    def post(self, request, *args, **kwargs):
        data = request.data
        dept_id = data.get("dept_id", 0)
        
        organization = kwargs.get("organization")

        if not organization.accepting_req:
            errors = [
                'This organization is not accepting requests currently.'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        department = kwargs.get("department")

        if  not department.organization == organization:
            errors = [
                'Invalid dept_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if request.user in department.requesting_users.all() or request.user == department.user:
            errors = [
                'Request already sent'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
        
        department.requesting_users.add(request.user.id)
        department.save()

        msgs = [
            'Join request sent'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)

class AssignedClass(views.APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="dept_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        dept_id = self.request.query_params.get('dept_id', "")

        if not dept_id:
            errors = [
                'dept_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        departments = models.Department.objects.filter(department_id=str(dept_id), is_active=True)
                
        if not len(departments):
            errors = [
                'Invalid dept_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        department = departments[0]

        qs = classes_models.Class.objects.filter(department=department, is_active=True)

        serializer = classes_serializers.ClassSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


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
            openapi.Parameter(name="dept_id", in_="query", type=openapi.TYPE_STRING),
            openapi.Parameter(name="sec_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        query_params = self.request.query_params
        dept_id = query_params.get('dept_id', None)
        sec_id = query_params.get('sec_id',None)

        if not dept_id:
            errors = [
                'dept_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not sec_id:
            errors = [
                'sec_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        departments = models.Department.objects.filter(Q(user__id=request.user.id) & Q(department_id=dept_id))

        if not len(departments):
            errors = [
                'Invalid dept_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        students = student_models.Student.objects.filter(
            Q(requested_section__id = sec_id) & Q(is_active=True)& Q(requested_section__of_class__department__department_id=dept_id)
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
            title = "Join Department request",
            type=openapi.TYPE_OBJECT,
            properties={
                'dept_id': openapi.Schema(type=openapi.TYPE_STRING),
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

    @validate_org
    @validate_dept
    def post(self, request, *args, **kwargs):
        data = request.data
        dept_id = data.get('dept_id',"")
        org_id = kwargs.get("org_id")
        students = str(data.get("students", "[]"))

        if not dept_id:
            errors = [
                'dept_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if len(students) < 3:
            errors = [
                "students not passed or students format should be like this. [1, 2, 3] where 1, 2 and 3 are student ID's"
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        departments = models.Department.objects.filter(Q(user__id=request.user.id) & Q(department_id=dept_id))

        if not len(departments):
            errors = [
                'Invalid dept_id'
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

        stud_qs = student_models.Student.objects.filter(is_active=True)

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
