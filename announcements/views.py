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
from teachers import models as teachers_models
from organizations import models as organizations_models
from sections import serializers as section_serializers

# Utils
import json
from utils.utilities import validate_user_type, pop_from_data
from utils.decorators import (
    validate_org,
    validate_dept,
    is_organization,
    is_department,
    is_teacher,
    is_org_or_department
)


class AnnouncenmentViewSet(views.APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters = [
            openapi.Parameter(name="id", in_="query", type=openapi.TYPE_STRING),
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
            openapi.Parameter(name="start_date", in_="query", type=openapi.FORMAT_DATE),
            openapi.Parameter(name="end_date", in_="query", type=openapi.FORMAT_DATE),
            openapi.Parameter(name="is_public", in_="query", type=openapi.TYPE_BOOLEAN),
        ]
    )
    def get(self, request,**kwargs):
        query_params = self.request.query_params
        
        id = query_params.get('id', None)
        org_id = query_params.get('org_id', None)
        start_date = query_params.get('start_date', None)
        end_date = query_params.get('end_date', None)
        is_public = query_params.get('is_public', None)

        qs = models.Announcement.objects.filter(is_active=True)

        if id:
            qs = qs.filter(id=int(id))

        if org_id:
            qs = qs.filter(organization__org_id=org_id)

        if start_date:
            qs = qs.filter(date__gte=start_date)
        
        if end_date:
            qs = qs.filter(date__lte=end_date)
        
        if is_public:
            if is_public == "true":
                qs = qs.filter(is_public=True)
            if is_public == "false":
                qs = qs.filter(is_public=False)
        

        serializer = serializers.AnnouncementSerializer(qs, many=True)
        return Response({'details': serializer.data}, status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Create Announcement",
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'user_type': openapi.Schema(type=openapi.TYPE_STRING),
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
    def post(self, request, **kwargs):
        data = request.data
        title = data.get('title', None)
        user_type = data.get('user_type', None)

        if not title or not user_type:
            errors = [
                'title and user_type are required'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        organization = kwargs.get("organization")

        if not validate_user_type(user_type, organization, request.user):
            errors = [
                'invalid user_type'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        data_dict = {
            "user": request.user.id,
            "organization": organization.id,
            "title": str(title),
        }

        serializer = serializers.AnnouncementSerializer(data=data_dict)
        if serializer.is_valid():
            serializer.save()
            msgs = [
                serializer.data
            ]
            return Response({'details': msgs}, status.HTTP_200_OK)

        errors = [
            str(serializer.errors)
        ]
        return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            title="Update Announcement",
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'data': openapi.Schema(type=openapi.TYPE_STRING),
                'date': openapi.Schema(type=openapi.FORMAT_DATE),
                'visible': openapi.Schema(type=openapi.TYPE_STRING),
                'is_public': openapi.Schema(type=openapi.TYPE_BOOLEAN),

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
    def put(self, request, *args, **kwargs):
        data = request.data
        id = data.get('id', None)

        if not id:
            errors = [
                'id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        announcements = models.Announcement.objects.filter(Q(id=int(id)) & Q(is_active=True) & Q(user=request.user))
        
        if not len(announcements):
            errors = [
                'invalid id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        announcement = announcements[0]

        serializer = serializers.AnnouncementSerializer(instance=announcement, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            msgs = [
                serializer.data
            ]
            return Response({'details': msgs}, status.HTTP_200_OK)

        errors = [
            str(serializer.errors)
        ]
        return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            title="Delete Announcement",
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'org_id': openapi.Schema(type=openapi.TYPE_STRING)
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
    def delete(self, request, *args, **kwargs):
        data = request.data
        id = data.get('id', None)

        if not id:
            errors = [
                'id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        announcements = models.Announcement.objects.filter(Q(id=int(id)) & Q(is_active=True) & Q(user=request.user))
        if not len(announcements):
            errors = [
                'invalid id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        announcement = announcements[0]
        announcement.is_active = False
        announcement.save()
        
        msgs = [
            "Successfully deleted announcement"
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)