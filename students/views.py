from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import status, permissions, authentication, views, viewsets
from rest_framework.response import Response
from . import models, serializers
from organizations import models as organizations_models
from sections import models as section_models
# Utils
import json

# Swagger
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi


class Student(views.APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.StudentSerializer

    @swagger_auto_schema(
        request_body = openapi.Schema(
            title = "Join teacher request",
            type=openapi.TYPE_OBJECT,
            properties={
                'sec_join_id': openapi.Schema(type=openapi.TYPE_STRING),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
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
        sec_join_id = data.get("sec_join_id")

        if not sec_join_id:
            errors = [
                'Sec_Join_ID  is not passed'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        sections = section_models.Section.objects.filter(join_id=sec_join_id)
        if not len(sections):
            errors = [
                'Invalid section Join ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        section = sections[0]

        if not section.is_active:
            errors = [
                'Invalid section Join ID'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        if not section.accepting_req:
            errors = [
                'This section is currently not accepting requests'
            ]
            return Response({'details': errors}, status.HTTP_400_BAD_REQUEST)

        data.update({
            "user": request.user.id,
            "requested_section": section.id
        })

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
