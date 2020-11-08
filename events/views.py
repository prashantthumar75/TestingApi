from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response

# Utils
import json
from . import models as events_models
from . import serializers as events_serializer
from subjects import models as subject_models
from teachers import models as teachers_models
from utils.decorators import validate_org, validate_event

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi


class Event(views.APIView):
    
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="event", in_="query", type=openapi.TYPE_INTEGER),
            openapi.Parameter(name="subject", in_="query", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        query_params = self.request.query_params
        event_id = query_params.get('event', None)
        subject_id = query_params.get('subject', None)

        qs = events_models.Event.objects.filter(is_active=True)

        if event_id:
            qs = qs.filter(id=event_id)

        if subject_id:
            qs = qs.filter(subject__id=int(subject_id))

        serializer = events_serializer.EventSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)



    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Create event",
            type=openapi.TYPE_OBJECT,
            properties={
                'type': openapi.Schema(type=openapi.TYPE_STRING),
                'data': openapi.Schema(type=openapi.TYPE_OBJECT),
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
        event_type = data.get("type","")
        event_data = data.get("data","")
        subject_id = data.get("subject_id","")
        date = data.get("date","")

        if not event_data or not event_type or not subject_id or not data:
            errors = [
                'event_data, event_type, subject_id and data are required'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        subjects = subject_models.Subject.objects.filter(is_active=True, id=subject_id)

        if not len(subjects):
            errors = [
                'Invalid subjects_id'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        subject = subjects[0]

        EVENT_TYPES_keys = [i[0] for i in events_models.EVENT_TYPES]
        if not str(event_type) in EVENT_TYPES_keys:
            errors = [
                f"invalid type, options are {EVENT_TYPES_keys}"
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)
        
        events_models.Event.objects.create(data=str(event_data), subject=subject, date=date, type=str(event_type))
        msgs = [ 
            'successfully created daily class'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)


class Assignment(views.APIView):
    
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("OK- Successful GET Request"),
            401: openapi.Response("Unauthorized- Authentication credentials were not provided. || Token Missing or Session Expired"),
            500: openapi.Response("Internal Server Error- Error while processing the GET Request Function.")
        },
        manual_parameters=[
            openapi.Parameter(name="assignment", in_="query", type=openapi.TYPE_INTEGER),
            openapi.Parameter(name="event", in_="query", type=openapi.TYPE_INTEGER),
            openapi.Parameter(name="subject", in_="query", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        query_params = self.request.query_params
        assignment_id = query_params.get('assignment', None)
        event_id = query_params.get('event', None)
        subject_id = query_params.get('subject', None)

        qs = events_models.Assignment.objects.filter(is_active=True)

        if assignment_id:
            qs = qs.filter(id=int(assignment_id))

        if event_id:
            qs = qs.filter(event__id=int(event_id))

        if subject_id:
            qs = qs.filter(event__subject__id=int(subject_id))

        serializer = events_serializer.AssignmentSerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Create Assignment",
            type=openapi.TYPE_OBJECT,
            properties={
                'org_id': openapi.Schema(type=openapi.TYPE_STRING),
                'event': openapi.Schema(type=openapi.TYPE_INTEGER),
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'due_date': openapi.Schema(type=openapi.FORMAT_DATETIME),
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
    @validate_event
    def post(self, request, *args, **kwargs):
        data = json.loads(json.dumps(request.data))
        title = data.get("title", "")
        description = data.get("description", "")
        due_date = data.get("due_date", "")

        event = kwargs.get("event")

        events_models.Assignment.objects.create(
            title = str(title),
            event = event,
            description = str(description),
            due_date = due_date
        )
        msgs = [ 
            'successfully created assignment'
        ]
        return Response({'details': msgs}, status.HTTP_200_OK)