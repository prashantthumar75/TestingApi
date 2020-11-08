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

class Section(views.APIView):

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
        ]
    )
    def get(self, request):
        query_params = self.request.query_params
        id = query_params.get('id', None)
        class_id = query_params.get('class_id', None)
        dept_id = query_params.get('dept_id', None)
        org_id = query_params.get('org_id', None)

        qs = models.Section.objects.filter(is_active=True)

        if id:
            qs = qs.filter(id=int(id))

        if class_id:
            qs = qs.filter(of_class__id=int(class_id))

        if dept_id:
            qs = qs.filter(of_class__department__department_id=dept_id)

        if org_id:
            qs = qs.filter(of_class__department__organization__org_id=org_id)

        serializer = serializers.SectionSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


# TODO: Can only be accessible by Organization
class CreateSection(views.APIView):
    serializer_class = serializers.SectionSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

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


class AssignTeacher(views.APIView):

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Assign class teacher to section",
            type=openapi.TYPE_OBJECT,
            properties={
                'teacher': openapi.Schema(type=openapi.TYPE_INTEGER),
                'section': openapi.Schema(type=openapi.TYPE_INTEGER)
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
        teacher = data.get('teacher', None)
        section = data.get('section', None)

        if not teacher or not section:
            errors = [
                "teacher and sction ID's are required"
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
        
        sections = models.Section.objects.filter(Q(id=int(section)) & Q(is_active=True))

        if not len(sections):
            errors = [
                "Invalid sction id"
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
        
        section = sections[0]

        teachers = teachers_models.Teacher.objects.filter(Q(id=int(teacher)) & Q(is_active=True))
        if not len(teachers):
            errors = [
                "Invalid teacher id"
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
        
        teacher = teachers[0]

        if section.class_teacher == teacher:
            errors = [
                "teacher is already assigned to this section"
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        section.class_teacher = teacher
        section.save()

        msgs = [
            'successfully assigned class teacher'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)