from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from . import models, serializers
from organizations import models as organizations_models
from sections import models as section_models
from django.db.models import Q

# Utils
import json
from utils.decorators import put_student, is_organization, validate_dept
from utils.utilities import pop_from_data

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi


class Student(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.StudentSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response(
                "Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="section_id", in_="query", type=openapi.TYPE_INTEGER),
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
            openapi.Parameter(name="dept_id", in_="query", type=openapi.TYPE_STRING),
            openapi.Parameter(name="class_id", in_="query", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        query_params = self.request.query_params
        org_id = query_params.get('org_id', None)
        section_id = query_params.get('section_id', None)
        dept_id = query_params.get('dept_id', None)
        class_id = query_params.get('class_id', None)

        qs = models.Student.objects.filter(is_active=True)

        if section_id:
            qs = qs.filter(section__id=section_id)
        if org_id:
            qs = qs.filter(section__of_class__department__organization__org_id=org_id)
        if dept_id:
            qs = qs.filter(section__of_class__department__department_id=dept_id)
        if class_id:
            qs = qs.filter(section__of_class__id=class_id)

        serializer = serializers.StudentSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Join teacher request",
            type=openapi.TYPE_OBJECT,
            properties={
                'sec_join_id': openapi.Schema(type=openapi.TYPE_STRING),
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

    def post(self, request):
        data = json.loads(json.dumps(request.data))
        sec_join_id = data.get("sec_join_id")

        if not sec_join_id:
            errors = [
                'Sec_Join_ID  is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        sections = section_models.Section.objects.filter(join_id=sec_join_id)
        if not len(sections):
            errors = [
                'Invalid section Join ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        section = sections[0]

        if not section.is_active:
            errors = [
                'Invalid section Join ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not section.accepting_req:
            errors = [
                'This section is currently not accepting requests'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        data.update({
            "user": request.user.id,
            "requested_section": section.id
        })

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Update Student",
            type=openapi.TYPE_OBJECT,
            properties={
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'phone': openapi.Schema(type=openapi.TYPE_INTEGER),
                'student_id': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response("OK- Successful POST Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            422: openapi.Response("Unprocessable Entity- Make sure that all the required field values are passed"),
            500: openapi.Response("Internal Server Error- Error while processing the POST Request Function.")
        }
    )
    @put_student
    def put(self, request, *args, **kwargs):
        data = request.data

        data = pop_from_data(["is_active", "user", "section"], data)

        student = kwargs.get("student")
        serializer = serializers.StudentSerializer(student,data=data, partial=True)

        if not serializer.is_valid():
            return Response({'details': [str(serializer.errors)]}, status.HTTP_400_BAD_REQUEST)

        serializer.save()
        msgs = [
            'successfully updated assignment'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            title="Delete Student",
            type=openapi.TYPE_OBJECT,
            properties={
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'sec_id': openapi.Schema(type=openapi.TYPE_STRING),
                'student_id': openapi.Schema(type=openapi.TYPE_STRING),
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
    @is_organization
    def delete(self, request, *args, **kwargs):
        data = request.data
        student_id = data.get('student_id', None)
        sec_id = data.get('sec_id', None)

        org = kwargs.get('organization')
        students = models.Student.objects.filter(Q(student_id=student_id) & Q(section__id=sec_id)& Q(section__of_class__department__organization__org_id=org.org_id)& Q(is_active=True))

        if not len(students):
            errors = [
                'invalid stduent id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        student = students[0]
        student.is_active = False
        student.save()

        msgs = [
            "Successfully deleted student"
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)
