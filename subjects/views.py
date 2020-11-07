from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from django.db.models import Q

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi

# CUSTOM
from . import models, serializers
from sections import models as sections_models
from users import permissions as custom_permissions



class Subject(views.APIView):

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
            openapi.Parameter(name="dept_id", in_="query", type=openapi.TYPE_STRING),
            openapi.Parameter(name="class_id", in_="query", type=openapi.TYPE_INTEGER),
            openapi.Parameter(name="section_id", in_="query", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        query_params = self.request.query_params
        id = query_params.get('id', None)
        section_id = query_params.get('section_id', None)
        class_id = query_params.get('class_id', None)
        dept_id = query_params.get('dept_id', None)
        org_id = query_params.get('org_id', None)

        qs = models.Subject.objects.filter(is_active=True)

        if id:
            qs = qs.filter(id=int(id))

        if section_id:
            qs = qs.filter(section__id=int(section_id))

        if class_id:
            qs = qs.filter(section__of_class__id=int(class_id))

        if dept_id:
            qs = qs.filter(section__of_class__department__department_id=dept_id)

        if org_id:
            qs = qs.filter(section__of_class__department__organization__org_id=org_id)


        serializer = serializers.SubjectSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class CreateSubject(views.APIView):
    serializer_class = serializers.SubjectSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, custom_permissions.IsOrganization)

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Create Subject",
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'section_id': openapi.Schema(type=openapi.TYPE_INTEGER)
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
        name = data.get('name', "")
        section_id = data.get('section_id', 0)

        if not name:
            errors = [
                'name is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not section_id:
            errors = [
                'section_id is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        qr_section = sections_models.Section.objects.filter(id=int(section_id), is_active=True)

        if not len(qr_section):
            errors = [
                'Invalid section_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)


        section_id = qr_section[0]

        if models.Subject.objects.filter(name=name, section=section_id).exists():
            errors = [
                'Subject already exists'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        models.Subject.objects.create(name=name, section=section_id)

        msgs = [
            'Successfully created subject'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)
