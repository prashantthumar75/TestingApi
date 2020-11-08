from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response

# Utils
import json
from . import models as event_models
from . import serializers as event_serializer
from subjects import models as subject_models

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi


class DailyClass(views.APIView):
    # queryset = event_models.Event.objects.filter(is_active=True)
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Create daily class event",
            type=openapi.TYPE_OBJECT,
            properties={
                'link': openapi.Schema(type=openapi.TYPE_STRING),
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'file': openapi.Schema(type=openapi.TYPE_FILE),
                'subject_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                'date': openapi.Schema(type=openapi.FORMAT_DATETIME),
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
        link = data.get("link","")
        title = data.get("title", "")
        description = data.get("description","")
        file = data.get("file","")
        subject_id = data.get("subject_id","")
        date = data.get("date","")

        if not link:
            errors = [
                'link is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not title:
            errors = [
                'title is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not description:
            errors = [
                'description is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not subject_id:
            errors = [
                'subject is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not date:
            errors = [
                'date is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        subjects = subject_models.Subject.objects.filter(is_active=True, id=subject_id)

        if not len(subjects):
            errors = [
                'Invalid subjects ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        subject = subjects[0]

        all_detail =  f' \
        link =  {str(link)} \n\
        title =  {str(title)} \n\
        description =  {str(description)} \n\
        file =  {str(file)}\n\
        '
        event_models.Event.objects.create(data=all_detail, subject=subject, date=date, type='RC')
        msgs = [ 
            'successfully created daily class'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)
