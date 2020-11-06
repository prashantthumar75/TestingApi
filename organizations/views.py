from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from django.db.models import Q

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi

# CUSTOM
from . import models
from teachers import models as teachers_models
from departments import serializers as departments_serializers
from departments import models as departments_models
from teachers import serializers as teachers_serializers
from users import models as users_models



# Utils
import json


class JoinRequestsDepartment(views.APIView):
    queryset = models.Organization.objects.filter(is_active=True)

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
    def get(self, request):
        query_params = self.request.query_params
        org_id = query_params.get('org_id', None)

        print(org_id)

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

        organization = organizations[0]

        departments = departments_models.Department.objects.filter(
            Q(organization__id=organization.id) & Q(is_active=True))

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
    def post(self, request):
        data = request.data
        org_id = data.get('org_id', "")
        dept_id = data.get('dept_id', "")
        requesting_user_id = data.get("requesting_user_id", 0)


        if not len(org_id):
            errors = [
                'org_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not len(dept_id):
            errors = [
                'dept_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not requesting_user_id:
            errors = [
                'requesting_user_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        organizations = self.queryset.filter(Q(user__id=request.user.id) & Q(org_id=org_id))

        if not len(organizations):
            errors = [
                'Invalid org_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        organization = organizations[0]

        departments = departments_models.Department.objects.filter(Q(organization__id=organization.id) & Q(department_id=dept_id))
        
        if not len(departments):
            errors = [
                'Invalid dept_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        department = departments[0]

        request_list = []
        for i in department.requesting_users.all():
            request_list.append(str(i.id))

        if not str(requesting_user_id) in request_list:
            errors = [
                'Invalid requesting_user_id ID'
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

    def get(self, request):
        org_id = request.data.get('org_id')

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

        teachers = teachers_models.Teacher.objects.filter(
            Q(requested_organization__id=organizations[0].id) & Q(is_active=True))

        serializer = teachers_serializers.TeacherSerializer(teachers, many=True)

        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request):
        data = json.loads(json.dumps(request.data))
        org_id = data.get('org_id')
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

        # issue teacher is not working
        if len(teachers) < 3:
            errors = [
                'teachers not passed'
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
                    'Invalid department ID'
                ]
                return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
            valid_teachers.append(temp_teach)

        for temp_teach in valid_teachers:
            temp_teach.organization = temp_teach.requested_organization
            temp_teach.requested_organization = None
            temp_teach.save()

        return Response({"details": ["Successfully accepted all provided requests."]}, status.HTTP_200_OK)
