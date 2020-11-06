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

# Utils
import json


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
    def post(self, request):
        data = request.data
        org_id = data.get("org_id", None)
        dept_id = data.get("dept_id", None)


        if not org_id:
            errors = [
                'org_id  is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
        
        organizations = organizations_models.Organization.objects.filter(org_id=org_id)
        if not len(organizations):
            errors = [
                'Invalid organization ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
        
        organization = organizations[0]

        if not organization.is_active:
            errors = [
                'Invalid organization ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not organization.accepting_req:
            errors = [
                'This organization is not accepting requests currently.'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        departments = models.Department.objects.filter(Q(organization=organization) & Q(department_id=dept_id) & Q(is_active=True))

        if not len(departments):
            errors = [
                'Invalid department ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
        
        department = departments[0]

        if not department.organization.accepting_req:
            errors = [
                "This organization is currently not accepting department's join requests"
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
