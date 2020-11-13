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
from utils.decorators import validate_org, validate_dept, is_organization, is_department, is_teacher, is_org_or_department

VISIBLE_TO = [
    ("ORG", 'ORG'),
    ("DEPT", 'DEPT'),
    ("TEACHER", 'TEACHER'),
    ("STUDENT", 'STUDENT'),
]

class OrganizationAnnouncenment(views.APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters = [
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
            openapi.Parameter(name="dept_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    @is_org_or_department
    def get(self, request,**kwargs):
        query_params = self.request.query_params

        org_id = kwargs.get('org_id')
        dept_id = kwargs.get('dept_id')

        organization = organizations_models.Organization.objects.filter(is_active=True)

        qs = models.Announcement.objects.filter(is_active=True)
        serializer = serializers.AnnouncementSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Create Organization Announcement",
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'visible': openapi.Schema(type=openapi.TYPE_STRING),
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
        title = data.get('title', "")
        description = data.get('description', "")
        org_id = kwargs.get("org_id")
        visible = data.get('visible',"")

        if not title:
            errors = [
                'title is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not visible:
            errors = [
                'title is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        VISIBLE_TO_keys = [i[0] for i in VISIBLE_TO]
        if not str(visible) in VISIBLE_TO_keys:
            errors = [
                f"invalid type, options are {VISIBLE_TO_keys}"
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
        else:
            models.Announcement.objects.create(title=title, visible=visible, description=description)

        msgs = [
            'successfully created Announcement for organization'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)
