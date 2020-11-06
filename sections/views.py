from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from django.db.models import Q

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi

# CUSTOM
from . import models, serializers
from teachers import models as teachers_models
from classes import models as class_models
from classes import serializers as class_serializers
from users import permissions as custom_permissions


class Section(views.APIView):

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
        qs = models.Section.objects.filter(is_active=True)
        serializer = serializers.SectionSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


# TODO: Can only be accessible by Organization
class CreateSection(views.APIView):
    serializer_class = serializers.SectionSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, custom_permissions.IsOrganization)

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Create Section",
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'of_class_id': openapi.Schema(type=openapi.TYPE_INTEGER)
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
        title = data.get('title', "")
        of_class_id = data.get('of_class_id', 0)

        if not title:
            errors = [
                'title is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not of_class_id:
            errors = [
                'of_class_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        qr_class = class_models.Class.objects.filter(id=int(of_class_id), is_active=True)

        if not len(qr_class):
            errors = [
                'Invalid of_class_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)


        of_class_id = qr_class[0]

        if models.Section.objects.filter(title=title, of_class=of_class_id).exists():
            errors = [
                'Section already exists'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        models.Section.objects.create(title=title, of_class=of_class_id)

        msgs = [
            'successfully created section'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)
