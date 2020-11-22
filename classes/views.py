from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from django.db.models import Q

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi

# CUSTOM
from . import models, serializers

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
        },
        manual_parameters=[
            openapi.Parameter(name="org_id", in_="query", type=openapi.TYPE_STRING),
            openapi.Parameter(name="dept_id", in_="query", type=openapi.TYPE_STRING),
        ]
    )
    @is_organization
    def get(self, request, **kwargs):
        query_params = self.request.query_params
        org_id = kwargs.get('organization', None)
        dept_id = query_params.get('dept_id',None)

        qs = models.Class.objects.filter(is_active=True, department__organization__id=org_id.id)

        if dept_id:
            qs = qs.filter(department__department_id=dept_id, department__organization__id=org_id.id)

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
    @validate_org
    @validate_dept
    def post(self, request, **kwargs):
        data = request.data
        title = data.get('title', "")

        department = kwargs.get("department")
        organization = kwargs.get("organization")

        if not title:
            errors = [
                'title is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if models.Class.objects.filter(title=title, department=department).exists():
            errors = [
                'Class already exists'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)


        data_dict = {
            "title": str(title),
            "department": department.id,
        }
        serializer = serializers.ClassSerializer(data=data_dict)
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
            title="Delete Class",
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
    @is_organization
    def delete(self, request, *args, **kwargs):
        data = request.data
        id = data.get('id', None)
        org_id = data.get('org_id', None)

        if not id:
            errors = [
                'id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        classes = models.Class.objects.filter(Q(id=int(id)) & Q(is_active=True) & Q(department__organization__org_id=org_id))
        if not len(classes):
            errors = [
                'invalid id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        classes = classes[0]
        classes.is_active = False
        classes.save()

        msgs = [
            "Successfully deleted class"
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)