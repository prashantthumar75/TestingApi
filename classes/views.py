from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from django.db.models import Q

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi

# CUSTOM
from . import models, serializers
from departments import models as departments_models
from organizations import models as organizations_models
from sections import serializers as section_serializers

# Utils
import json
from utils.decorators import validate_org, validate_dept, is_organization, is_department

class ClassViewSet(views.APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        }
    )
    def get(self, request):
        qs = models.Class.objects.filter(is_active=True)
        serializer = serializers.ClassSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Create Class",
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
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
    @is_department
    @validate_org
    def post(self, request, **kwargs):
        data = request.data
        title = data.get('title', "")
        department = data.get('dept_id', "")

        org_id = kwargs.get("org_id")

        if not title:
            errors = [
                'title is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not department:
            errors = [
                'department is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        departments = departments_models.Department.objects.filter(department_id = department)
        if not len(departments):
            errors = [
                'Invalid department'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        department = departments[0]
        if models.Class.objects.filter(title=title, department=department).exists():
            errors = [
                'Class already exists'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        models.Class.objects.create(title=title, department=department)

        msgs = [
            'successfully created class'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)
