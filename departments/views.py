from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from django.db.models import Q

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi

# Custom
from . import models, serializers
from organizations import models as organizations_models
from classes import models as classes_models
from classes import serializers as classes_serializers

from utils.decorators import validate_dept, validate_org

# Utils
import json

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

        departments = models.Department.objects.filter(id=int(dept_id), is_active=True)
                
        if not len(departments):
            errors = [
                'Invalid dept_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        department = departments[0]

        qs = classes_models.Class.objects.filter(department=department, is_active=True)

        serializer = classes_serializers.ClassSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)